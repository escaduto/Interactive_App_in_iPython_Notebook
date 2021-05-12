# Creating Interactive Applications in an iPython Notebook via ipywidget, folium, and API</u>

## Table of Contents  
- [Setup](#Setup)  
- [Project Details](#project-details)  
- [Primary Packages](#primary-packages) 
- [Walk-Through](#walk-through)  
___


## Setup

Create an `.env` file by copying the `.env.example` and renaming it to `.env`. Replace the keys with your API_KEY

## Project Details

## Primary Packages & Tools

## Walk-Through

1. <b>Interactive mapping</b> 

Interactive search through all the campground facilities across the state of California. Folium has extensions to easily add various tools within the map, most notable is the reverse geocoding functionality. The pop-up information card for each facility location contains the attributes including its unique ID, number of campsites, as well as the description from the recreation.gov site. 

<img src="docs/gif/tab1_search_A.gif" alt="tab1_search_A">


<br><br>

2. <b>Filtering Search</b>

The ipywidget package enables interactive and immersive user experience, allowing increased control over data filteration, visualization aspects. The widgets can be used to specify user-selected campground, after using the interactive map to inform their decision. The additional attributes include: use type (e.g. overnight or day-use), pets allowed, number of people, number of vehicles, primary equipment of use (e.g. RV, Tent, Trailer). 


<img src="docs/gif/tab1_search_B.gif" alt="tab1_search_B">

<br><br>
3. <b>Visualizing Search </b>



<img src="docs/gif/tab2_selection_A.gif" alt="tab2_selection_A">

<br><br>
4. <b>Accessing Real-Time Data</b>

Webscraping 

<img src="docs/gif/tab2_selection_B.gif" alt="tab2_selection_B">

<br><br>
5. <b>Visualization</b>

After 

<img src="docs/gif/tab3_results_A.gif" alt="tab3_results_A">

<br><br>
6. <b>Compilation of search results</b>

Additional searches can be consolidated in the Availability tab for the purpose of allowing the user to compare between several campgrounds of interest. 

<img src="docs/gif/tab3_results_B.gif" alt="tab3_results_B">
