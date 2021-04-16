import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import json

def convert_df_to_gdf(df, lon, lat): 
    gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df[lon], df[lat]))
    return gdf

def revert_gdf_to_df(geoDF): 
    df = pd.DataFrame(geoDF.drop(columns='geometry'))
    return df

def filter_CA_bounds(df, lon, lat):
    geoDF = convert_df_to_gdf(df, lon, lat)

    state_path = '../data/CA_Extent/California_5kmbuff.shp'
    CA_states = gpd.read_file(state_path)
    
    geoDF = geoDF.set_crs("EPSG:4326")
    CA_states = CA_states.to_crs(geoDF.crs)

    clipped_gpd = gpd.overlay(geoDF, CA_states, how='intersection')
    clipped_df = revert_gdf_to_df(clipped_gpd)
    return clipped_df

def convert_csv_to_geojson(file_nm, keep_columns, out_nm, longitude, latitude): 
    df = clean_df(file_nm, keep_columns)
    gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df[longitude], df[latitude]))

    gdf.to_file(out_nm, driver='GeoJSON')
    return out_nm

def clean_df(file_nm, keep_columns):
    df = pd.read_csv(file_nm)
    df = df[keep_columns]
    return df 
