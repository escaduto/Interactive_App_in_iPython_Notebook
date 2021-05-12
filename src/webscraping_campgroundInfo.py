import urllib3, re
from bs4 import BeautifulSoup
import pandas as pd 
import geopandas as gpd
import json

"""
Consolidate campsite information from rec.gov site into database. 
information on: dog friendliness, reservation fee, availability, amenities, activities/highlights
RV/car accessibility, satellite map, weather (?), coordinates
"""

def access_website(url):
     req = urllib3.PoolManager()
     res = req.request('GET', url)
     soup = BeautifulSoup(res.data, 'html.parser')
     return soup

def get_unique_campsite_url(root_url):
    camp_name = [] 
    url_list = [] 
    camp_ID = [] 
    region_list = [] 
    price_rng = [] 
    latitude = [] 
    longitude = [] 

    for i in range(231800, 234800 + 1): #10067346, 258815, 250000, 10004152 
        try: 
            url = root_url + str(i) 
            soup = access_website(url)
            nm = soup.find('h1').text
            if nm != "":
                cont = soup.find_all('div', attrs = {'id': 'coordinates'})
                lat = re.search('latitude":(.*),"long', str(soup)).group(1)
                lon = re.search('longitude":(.*)},"has', str(soup)).group(1)
                price = re.search('priceRange":"(.*)","tel', str(soup)).group(1)
                rgn = re.search('"addressRegion":"(.*)","po', str(soup)).group(1)

                print(nm, lat, lon, price, rgn)

                camp_name.append(nm)
                url_list.append(url)
                camp_ID.append(str(i))
                latitude.append(lat)
                longitude.append(lon)
                price_rng.append(price)
                region_list.append(rgn)

        except: 
            pass

        
    df = pd.DataFrame.from_dict({
            'ID': camp_ID, 
            'Name' : camp_name, 
            'URL' : url_list,
            'Region' : region_list,
            'Latitude': latitude, 
            'Longitude': longitude, 
            'Price Range': price_rng, 
            })
    
    df.to_csv('camp_info.csv', index=False) 



def get_key(val, my_dict):
    dates_lst = [] 
    for key, value in my_dict.items():
         if val == value:
             dates_lst.append(key)
    return dates_lst
 

def get_availability(facilityid, camp_id_lst, start_dt, end_dt, campsite_nm):
    camp_name = [] 
    avail = []
    reserv =[]
    nonreserv =[]
    
    
    campsite_df = gpd.read_file(campsite_nm)
    
    for camp_id in camp_id_lst:   
        print(camp_id)     
        df = campsite_df[(campsite_df['FacilityID'].astype(str) == facilityid) & (campsite_df['CampsiteName'].astype(str) == camp_id)]
        campsite_name = df.iloc[0]['CampsiteID']
        url = f'https://www.recreation.gov/api/camps/availability/campsite/{campsite_name}?start_date={start_dt}T00%3A00%3A00.000Z&end_date={end_dt}T00%3A00%3A00.000Z'
        soup = access_website(url)
        j = json.loads(soup.text)
        raw_dic = j['availability']['availabilities']
        
        camp_name.append(camp_id)
        avail.append(get_key('Available', raw_dic))
        reserv.append(get_key('Reserved', raw_dic))
        nonreserv.append(get_key('Not Reservable', raw_dic))
        
    avail_dic = {'CampsiteName': camp_name, 'Available': avail, 'Reserved': reserv, 'Not Reservable': nonreserv}   

    return avail_dic

        

        
# new_avail = {'Available' : avail_dic["Available"] + get_key('Available', raw_dic)}
# new_reserv = {'Reserved' : avail_dic["Reserved"] + get_key('Reserved', raw_dic)}
# new_noreserv = {'Not Reservable' : avail_dic["Not Reservable"] + get_key('Not Reservable', raw_dic)}
