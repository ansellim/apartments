# Ansel Lim
# 24 Nov 2021
# Combine df.csv (Condo data) and df_hdb.csv (HDB data) and add quality data.

import pandas as pd

df_condo = pd.read_csv('../data/processed/df.csv')
df_hdb = pd.read_csv('../data/processed/df_hdb.csv')
df_condo = df_condo[['street', 'project', 'marketSegment','lat', 'long', 'avg_price_per_sqm', 'district',
                     'commonest_tenure', 'num_malls', 'num_taxi_stands','num_primary_schools',
                     'num_mrt', 'num_hawker', 'num_carparks','num_bus_stops', 'num_chas_clinics',
                     'num_sports_facilities','num_community_centers', 'num_supermarkets', 'num_secondary_schools',
                     'num_eating_establishments', 'num_eating_establishments_', 'num_parks']]
df_hdb = df_hdb[['block', 'floor_area_sqm',
       'resale_price', 'price_per_sqm', 'lat', 'long', 'isLatLongAvailable',
       'num_malls', 'num_taxi_stands', 'num_primary_schools', 'num_mrt',
       'num_hawker', 'num_carparks', 'num_bus_stops', 'num_chas_clinics',
       'num_sports_facilities', 'num_community_centers', 'num_supermarkets',
       'num_secondary_schools', 'num_eating_establishments', 'num_parks']]

df_condo.rename(columns={'avg_price_per_sqm':'price_per_sqm'},inplace=True)
df_condo.drop(columns=['street','marketSegment'],inplace=True)