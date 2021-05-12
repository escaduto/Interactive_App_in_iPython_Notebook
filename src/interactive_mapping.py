import folium
from folium.plugins import MarkerCluster
from folium import IFrame, plugins, Figure
from geoprocessing import convert_csv_to_geojson
import geopandas as gpd
import io
from PIL import Image
import numpy as np


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

# icons for facilities, campgrounds, visitor center, etc. 
# campsites icons 
# label with name, amentities 

def add_facilities_icon(df):
    facility_icon_dict = {'Facility': 'glyphicon glyphicon-tent', 'Campground': 'glyphicon glyphicon-tent', 'Permit': 'glyphicon glyphicon-tent', 'Activity Pass': 'glyphicon glyphicon-tent',
       'Visitor Center': 'glyphicon glyphicon-tent', 'Ticket Facility': 'glyphicon glyphicon-tent', 'Library': 'glyphicon glyphicon-tent', None : 'glyphicon glyphicon-tent'}
    df["FacilityTypeIcon"] = df["FacilityTypeDescription"].map(facility_icon_dict)
    return df 


def add_campsite_popupinfo(df):
    cols = ['CampsiteName', 'CampsiteType', 'TypeOfUse', 'Checkin Time', 'Checkout Time', 'Pets Allowed', 'EquipmentsAllowed', 'Max Num of Vehicles', 'Max Num of People']
    df['popup_info'] = df[cols].apply(lambda row: f"___________________________________________ <br> \
                                                    Campsite Name: {row.values[0]} <br> \
                                                        CampsiteType: {row.values[1]} <br> \
                                                            Type Of Use: {row.values[2]} <br> \
                                                                Checkin Time: {row.values[3]} <br> \
                                                                    Checkout Time: {row.values[4]} <br> \
                                                                        Pets Allowed: {row.values[5]} <br> \
                                                                            EquipmentsAllowed: {row.values[6]} <br> \
                                                                                Max Num of Vehicles: {row.values[7]} <br> \
                                                                                    Max Num of People: {row.values[8]} <br> \
                                                                                        ___________________________________________ <br> \
                                                            ", axis=1)
    return df 

def get_map_center(gpd_df):
    center_pnt = gpd_df['geometry'].unary_union.convex_hull.centroid

    return [center_pnt.y, center_pnt.x]


def interactive_facilities_map(facilities_nm):
    facilities = gpd.read_file(facilities_nm)
    facilities = add_facilities_icon(facilities)
    
    map_center = get_map_center(facilities)
    maploc = folium.Map(location=map_center, zoom_start=6, prefer_canvas=True, tiles="Stamen Terrain")
    marker_cluster = MarkerCluster().add_to(maploc)

    facility_locations = facilities[['FacilityLatitude', 'FacilityLongitude']]
    fclty_pnts = facility_locations.values.tolist()

    for fc_pnt in range(0, len(fclty_pnts)):
        f = folium.Figure()

        # add campsite mini map into popup window (due to high load times, this feature was removed)
        # facility_id = facilities['FacilityID'][fc_pnt]
        # campsite_map = interactive_campsite_map(campsite_nm, facility_id)
        # campsite_map.add_to(f)

        facility_popup_info = f"___________________________________________________________________________________________ <br> \
                                            <b style='color:Tomato;'>Facility Name:</b> {facilities['FacilityName'][fc_pnt]} <br><br> \
                                                    <b style='color:Tomato;'>Facility ID:</b>  {facilities['FacilityID'][fc_pnt]} <br><br> \
                                                        <b style='color:Tomato;'>Facility Type:</b>  {facilities['FacilityTypeDescription'][fc_pnt]} <br><br> \
                                                            <b style='color:Tomato;'> Total Campsites:</b>  {facilities['TotalCampsites'][fc_pnt]} <br><br> \
                                                                <b style='color:Tomato;'>Reservable:</b> {facilities['Reservable'][fc_pnt]} <br><br> \
                                                                    {facilities['FacilityDescription'][fc_pnt]} <br><br>\
                                                                ___________________________________________________________________________________________ <br>"
        iframe = folium.IFrame(html=facility_popup_info, width=500, height=300)
        f.add_to(iframe)
        popup = folium.Popup(iframe, max_width=2650)

        facility_icon = folium.Icon(color = 'green')#icon= facilities['FacilityTypeIcon'][fc_pnt], icon='map-pin', prefix='fa')          
        folium.Marker(fclty_pnts[fc_pnt], popup= popup, icon = facility_icon, tooltip=facilities['FacilityName'][fc_pnt]).add_to(marker_cluster)
    
    plugins.Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    ).add_to(maploc)

    minimap = plugins.MiniMap()
    maploc.add_child(minimap)
    plugins.Geocoder().add_to(maploc)

    maploc.save("../docs/facility_map.html")
    return maploc


def interactive_campsite_map(campsite_lst, campsite_nm, facility_id):
    campsites = gpd.read_file(campsite_nm)
    campsites = add_campsite_popupinfo(campsites)

    if facility_id != None: 
        campsites = campsites[campsites['FacilityID'] == facility_id]
        campsites['selected_campsite'] = campsites.CampsiteName.isin(campsite_lst)
        campsites['icon_color'] = np.where((campsites.selected_campsite == True), '#ed7d08', '#738678')
        campsites['icon_size'] = np.where((campsites.selected_campsite == True), 10, 5)
        campsites['icon_icon'] = np.where((campsites.selected_campsite == True), 'anchor', 'times')

        map_center = get_map_center(campsites)
        maploc = folium.Map(location=map_center, zoom_start=17, prefer_canvas=True)

    # return campsites[['selected_campsite', 'icon_color', 'icon_size', 'icon_icon']]
    campsites_locations = campsites[['CampsiteLatitude', 'CampsiteLongitude']]
    cmpsites_pnts = campsites_locations.values.tolist()

    for cmp_pnt in range(0, len(cmpsites_pnts)):
        # campsite_icon = folium.Icon(icon_color = 'black', fill_color=campsites['icon_color'].iloc[cmp_pnt], \
        #                 icon=campsites['icon_icon'].iloc[cmp_pnt], fill_rule='evenodd') 
        
        campsite_popup_info = campsites['popup_info'].iloc[cmp_pnt]
        folium.Circle(cmpsites_pnts[cmp_pnt], popup= campsite_popup_info, radius = float(campsites['icon_size'].iloc[cmp_pnt]), fill = True, fillOpacity=1,\
                                            weight = 3, color = campsites['icon_color'].iloc[cmp_pnt], \
                                            tooltip=campsites['CampsiteName'].iloc[cmp_pnt]).add_to(maploc)

    return maploc

    
