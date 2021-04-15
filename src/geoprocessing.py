import geopandas as gpd
import pandas as pd

def convert_df_to_gdf(df, lon, lat): 
    gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df[lon], df[lat]))
    return gdf

def revert_gdf_to_df(geoDF): 
    df = pd.DataFrame(geoDF.drop(columns='geometry'))
    return df

def filter_CA_bounds(df, lon, lat):
    geoDF = convert_df_to_gdf(df, lon, lat)

    state_path = '..data/CA_Extent/California_5kmbuff.shp'
    CA_states = gpd.read_file(state_path)

    CA_states = CA_states.to_crs('EPSG:3310')
    geoDF = geoDF.to_crs('EPSG:3310')

    clipped_gpd = gpd.overlay(geoDF, CA_states, how='intersection')
    clipped_df = revert_gdf_to_df(clipped_gpd)
    return clipped_df

