# 31 Oct / 1 Nov 2021
# Ansel Lim
# with reference to https://gis.stackexchange.com/questions/349637/given-list-of-points-lat-long-how-to-find-all-points-within-radius-of-a-give
# as well as https://stackoverflow.com/questions/58548566/selecting-rows-in-geopandas-or-pandas-based-on-latitude-longitude-and-radius
# https://gis.stackexchange.com/questions/381639/how-to-draw-radius-buffer-around-the-points-and-perform-intersection-with-other
# https://gis.stackexchange.com/questions/395185/buffer-is-too-large-because-of-crs
# https://gis.stackexchange.com/questions/383014/how-to-use-geopandas-buffer-function-to-get-buffer-zones-in-kilometers

import pandas as pd
import geopandas as gpd
import shapely

ura = pd.read_csv("./data/ura.csv")
bus_stops = pd.read_csv("./data/bus_stops.csv")

geom_list_ura = [shapely.geometry.Point(lon,lat) for lon,lat in zip(ura["long"],ura["lat"])]
gdf = gpd.GeoDataFrame(ura, geometry=geom_list_ura, crs={"init":"epsg:32648"})
gdf_proj = gdf.to_crs({"init": "epsg:32648"})

# alternative method
# gdf2 = gpd.GeoDataFrame(ura,geometry=gpd.points_from_xy(ura["long"],ura["lat"]),crs={"init":"epsg:32648"})
# gdf2 = gdf2.to_crs({"init": "epsg:32648"})

geom_list_bus_stops = [shapely.geometry.Point(lon,lat) for lon,lat in zip(bus_stops["Longitude"],bus_stops["Latitude"])]
gdf_bus_stops = gpd.GeoDataFrame(bus_stops, geometry=geom_list_bus_stops , crs={"init":"epsg:32648"})
gdf_proj_bus_stops = gdf_bus_stops.to_crs({"init": "epsg:32648"})

gdf_proj['geometry']=gdf_proj['geometry'].buffer(1000,16)

#note: Spatial indexes require either `rtree` or `pygeos`. See installation instructions at https://geopandas.org/install.html
intersection = gpd.sjoin(gdf_proj,gdf_proj_bus_stops,
                         how='left'
                         ,predicate='contains')

print(intersection.shape)