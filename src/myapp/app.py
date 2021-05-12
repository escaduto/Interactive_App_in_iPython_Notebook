# from webscraping_campgroundInfo import get_unique_campsite_url
# get_unique_campsite_url(root_url = "https://www.recreation.gov/camping/campgrounds/") 

import folium
from flask import Flask, render_template
from interactive_mapping import interactive_facilities_map, interactive_campsite_map

campsite_nm = '/Users/erica/Documents/projects/all_camp/data/complete_campsites_CA.geojson'
facilities_nm = '/Users/erica/Documents/projects/all_camp/data/complete_facility_CA.geojson'

app = Flask(__name__)

@app.route('/')
def index():
    facility_id = '232893'
    folium_map = interactive_campsite_map(campsite_nm, facility_id)
    folium_map.save('/Users/erica/Documents/projects/all_camp/src/myapp/templates/map.html')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)