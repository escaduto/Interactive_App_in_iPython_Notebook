import urllib3, re
from bs4 import BeautifulSoup
import pandas as pd 

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





