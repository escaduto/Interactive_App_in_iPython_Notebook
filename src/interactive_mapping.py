import folium
from folium.plugins import MarkerCluster
from geoprocessing import convert_csv_to_geojson
import geopandas as gpd
import io
from PIL import Image


# clean df 
keep_columns_1 = ['CampsiteID', 'FacilityID', 'CampsiteName', 'CampsiteType', 'TypeOfUse', 
    'Loop', 'CampsiteLongitude', 'CampsiteLatitude', 'Site Width', 'IS EQUIPMENT MANDATORY', 
    'Checkout Time', 'Pets Allowed', 'Checkin Time', 'Min Num of People', 'Max Num of People', 
    'Site Length', 'Max Num of Vehicles', 'EquipmentsAllowed', 'Campfire Allowed']
keep_columns_2 = ['FacilityID', 'FacilityName', 'FacilityDescription',
       'ParentRecAreaID', 'FacilityTypeDescription', 'FacilityLongitude',
       'FacilityLatitude', 'Reservable', 'STATE_NAME']
# convert_csv_to_geojson('../data/campsites_CA.csv', keep_columns_1, '../data/campsites_CA.geojson', 'CampsiteLongitude', 'CampsiteLatitude')
# convert_csv_to_geojson('../data/facilities_CA.csv', keep_columns_2, '../data/facilities_CA.geojson', 'FacilityLongitude', 'FacilityLatitude')

def interactive_map(campsite_nm, facilities_nm):
    if campsite_nm.endswith('.geojson') and facilities_nm.endswith('.geojson'):
        campsites = gpd.read_file(campsite_nm)
        facilities = gpd.read_file(facilities_nm)

        maploc = folium.Map(location=[38.542145, -122.657199],zoom_start=13,tiles="Stamen Toner")

        marker_cluster = MarkerCluster().add_to(maploc)

        locations = campsites[['CampsiteLatitude', 'CampsiteLongitude']]
        locationlist = locations.values.tolist()

        for point in range(0, len(locationlist)):
            folium.Marker(locationlist[point], popup=campsites['CampsiteName'][point]).add_to(marker_cluster)

        folium.GeoJson(
        facilities,
        style_function=lambda feature: {
            'fillColor': '#b14e12',
            'color' : '#b11225',
            'weight' : 1,
            'fillOpacity' : 0.5,
            }
        ).add_to(maploc)

        maploc.save("../docs/campsite_map.html")
        return maploc

    
