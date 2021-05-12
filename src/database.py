import datetime, sqlite3, requests, json, os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from geoprocessing import filter_CA_bounds
from dotenv import load_dotenv
from collections import defaultdict

# 1) access RIDB API [OK]
# 2) connect to sqlite db [OK]
# 3) create SQL database to save facilities (campground) data within CALIFORNIA [OK]
# 4) create SQL database to save campsite data based on facilities ID [OK]
# 5) clean and combined attributes into main.db and perform queries  
# 6) based on user inputted campsite, get availability (based on another api) 
# 7) email availability + site descriptions + possible closures/warnings 
# 8) perform cron job to auto send availability of campsite @7:15am 

cwd = os.getcwd()
#-------------------------------------------------------------------------------------#
# 1) access RIDB API from RIDB_access.py
load_dotenv()
apikey = os.getenv('API_KEY')

def access_RIDB_API(url):
    headers = { 'apikey' :  apikey} 
    r = requests.get(url, headers=headers, verify=True)
    j = json.loads(r.text)
    return j

#-------------------------------------------------------------------------------------#
# 2) connect to sqlite db 
connection = sqlite3.connect(os.path.join(cwd, "../data/data.db"))

#-------------------------------------------------------------------------------------#
# 3) create SQL database to save facilities (campground) data 

def drop_table_sql(tablename):
    '''
    drops table specified in argument 
    '''
    DROP_TABLE = f"""DROP TABLE IF EXISTS {tablename}"""
    return DROP_TABLE


def create_input(raw_dict, my_dict, key_attribute):
    '''
    creates df from json to dict raw files from api dump
    '''
    getValues = lambda key,inputData: [subVal[key] for subVal in inputData if key in subVal]

    for attr in my_dict: 
        lst = getValues(attr, raw_dict[key_attribute])
        my_dict[attr].extend(lst)
    
    df = pd.DataFrame.from_dict(my_dict)

    return df


def create_facilities_db():
    '''
    creates db in sqlite from pandas df from RIDB API for all facilities in ca 
    '''

    complete_df = pd.DataFrame()
    counter += 1 
    for i in range(0, 20000 + 1, 50):
        counter += 1 
        url = f'https://ridb.recreation.gov/api/v1/facilities?limit=50&offset={str(i)}'

        facilities_dict = access_RIDB_API(url)

        if len(facilities_dict['RECDATA']) == 0:
            break 

        my_dict = {"FacilityID": [],"FacilityName":[], "FacilityDescription":[], 'ParentRecAreaID': [] ,
        "FacilityTypeDescription":[], "FacilityLongitude":[], "FacilityLatitude":[], 'Reservable': []}

        input_df = create_input(raw_dict = facilities_dict, my_dict = my_dict, key_attribute = 'RECDATA')
        frames = [complete_df, input_df]
        complete_df = pd.concat(frames)
    
    complete_df.to_csv('../data/facilities_Nationwide.csv')

    CA_DF = filter_CA_bounds(complete_df, 'FacilityLongitude', 'FacilityLatitude')
    CA_DF.to_csv('../data/facilities_CA.csv')

    all_CA_facility_id = pd.unique(CA_DF['FacilityID']).tolist()

    with connection:
        connection.execute(drop_table_sql('facilities_db'))
        e = create_engine('sqlite:///data/data.db') 
        CA_DF.to_sql(name='facilities_db', con=connection)

    return all_CA_facility_id

#-------------------------------------------------------------------------------------#

# 4) create SQL database to save campsite data based on facilities ID 

def getAttributesVals(df):
    
    attr_df1 = pd.DataFrame()
    for index, row in df.iterrows(): 
        try: 
            attr_name = [d['AttributeName'] for d in row['ATTRIBUTES']]
            attr_val = [d['AttributeValue'] for d in row['ATTRIBUTES']]
            equip_val = [d['EquipmentName'] for d in row['PERMITTEDEQUIPMENT']]

            attr_tuple = list(zip(attr_name, attr_val))
            
            orDict = defaultdict(list)
            for key, val in attr_tuple:
                orDict[key].append(val)
            orDict['CampsiteID'] = row['CampsiteID']

            if len(equip_val) == 0:
                orDict['EquipmentsAllowed'] = None
            else: 
                orDict['EquipmentsAllowed'] = ', '.join(equip_val)

            attr_df2 = pd.DataFrame.from_dict(orDict)
            frames = [attr_df1, attr_df2]
            attr_df1 = pd.concat(frames)
        except: 
            print("error at",  index, row) # some campsite attributes dont have additional information for equipments and amenities 
            pass

    return attr_df1


def create_campsites_db(all_facility_id):
    '''
    creates db in sqlite from pandas df from RIDB API for all campsites in ca based on facilities list 
    '''
    complete_df = pd.DataFrame()
    ttl_ids = len(all_facility_id)
    counter =  0 
    for ids in all_facility_id:
        counter += 1 
        print(f"getting campsites for facility id: {ids}")
        for i in range(0, 1000 + 1, 50):
            url = f'https://ridb.recreation.gov/api/v1/facilities/{ids}/campsites?limit=50&offset={str(i)}'

            campsites_dict = access_RIDB_API(url)
            if len(campsites_dict['RECDATA']) == 0:
                break 

            print(f"{round(counter/ttl_ids * 100, 3)}%", counter, ids, i)
            my_dict = {"CampsiteID": [],"FacilityID":[], "CampsiteName":[], 'CampsiteType': [] ,
            "TypeOfUse":[], "Loop":[], "CampsiteLongitude":[], 'CampsiteLatitude': [], 'ATTRIBUTES': [], 'PERMITTEDEQUIPMENT' : []}

            input_df = create_input(raw_dict = campsites_dict, my_dict = my_dict, key_attribute = 'RECDATA')
            frames = [complete_df, input_df]
            complete_df = pd.concat(frames)

    print("saving new campsites dataframe into csv")
    complete_df.to_csv('../data/campsites_CA_RAW.csv')

    attributes_df = getAttributesVals(complete_df)

    # make sure key column type matches before merging 
    attributes_df['CampsiteID'] = attributes_df['CampsiteID'].astype(int)
    complete_df['CampsiteID'] = complete_df['CampsiteID'].astype(int)

    # drop attributes column; format cannot be read by sqlite
    complete_df = complete_df.drop(columns = ['ATTRIBUTES', 'PERMITTEDEQUIPMENT'])

    # merge attributes with main df 
    complete_df = complete_df.merge(attributes_df, on='CampsiteID', how='left')
    
    # drop any dupe entries 
    complete_df = complete_df.drop_duplicates() 

    print("saving new campsites dataframe into csv")
    complete_df.to_csv('../data/campsites_CA.csv')

    with connection:
        print("connecting to sqlite database...")
        connection.execute(drop_table_sql('campsites_db'))
        print("creating engine...")
        e = create_engine('sqlite:///data/data.db') 
        print("saving dataframe into database...")
        complete_df.to_sql(name='campsites_db', con=connection)
        print("complete!")


#-------------------------------------------------------------------------------------#

# 5) After connected to sqlite, create db for facilities and campsites 

all_CA_facility_id = create_facilities_db()

GET_ALL_FACILITIES_ID = """ SELECT FacilityID FROM facilities_db """

with connection:
    print("connecting to sqlite database...")
    all_CA_facility_id = connection.execute(GET_ALL_FACILITIES_ID).fetchall()
    del all_CA_facility_id[54] # invalid id (alphanumeric) 
    print("retrieving facilities id in California.")
    all_CA_facility_id = [int(a_tuple[0]) for a_tuple in all_CA_facility_id]

# create_campsites_db(all_CA_facility_id) 

#6) add facilities name, lat/long based on ID into campsite csv 




