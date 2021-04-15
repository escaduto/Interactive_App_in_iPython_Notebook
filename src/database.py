import datetime, sqlite3, requests, json
import pandas as pd
from sqlalchemy import create_engine
import os 
from geoprocessing import filter_CA_bounds
from dotenv import load_dotenv

# 1) access RIDB API from RIDB_access.py [OK]
# 2) connect to sqlite db [OK]
# 3) create SQL database to save facilities (campground) data within CALIFORNIA [OK]
# 4) create SQL database to save campsite data based on facilities ID [OK]
# 5) perform queries  

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

    for i in range(-50, 20000 + 1, 50):
        url = f'https://ridb.recreation.gov/api/v1/facilities?limit=50&offset={str(i)}'

        facilities_dict = access_RIDB_API(url)

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

    return all_facility_id

#-------------------------------------------------------------------------------------#

# 4) create SQL database to save campsite data based on facilities ID 

def create_campsites_db(all_facility_id):
    '''
    creates db in sqlite from pandas df from RIDB API for all campsites in ca based on facilities list 
    '''

    complete_df = pd.DataFrame()
    
    for ids in all_facility_id:
        for i in range(-50, 200 + 1, 50):
            url = f'https://ridb.recreation.gov/api/v1/facilities/{ids}/campsites?limit=50&offset={str(i)}&offset=0'

            campsites_dict = access_RIDB_API(url)

            my_dict = {"CampsiteID": [],"FacilityID":[], "CampsiteName":[], 'CampsiteType': [] ,
            "TypeOfUse":[], "Loop":[], "CampsiteLongitude":[], 'CampsiteLatitude': []}

            input_df = create_input(raw_dict = campsites_dict, my_dict = my_dict, key_attribute = 'RECDATA')
            frames = [complete_df, input_df]
            complete_df = pd.concat(frames)
    
    complete_df.to_csv(os.path.join(cwd, 'data/campsites_CA.csv'))

    with connection:
        connection.execute(drop_table_sql('campsites_db'))
        e = create_engine('sqlite:///data/data.db') 
        complete_df.to_sql(name='campsites_db', con=connection)

#-------------------------------------------------------------------------------------#

# 5) After connected to sqlite, create db for facilities and campsites 
all_facility_id = create_facilities_db()
# create_campsites_db(all_facility_id) 

#6) add facilities name, lat/long based on ID into campsite csv 



