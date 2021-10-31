# Ansel Lim
# 31 October 2021
# process the data after obtaining data with get_data.py

import pickle
import pandas as pd

class DataProcessor:
    def __init__(self, pickled_loader="cached_data"):
        self.pickled_loader = pickled_loader
        self.data = None

    def load(self):
        cls = pickle.load(open(self.pickled_loader, "rb"))
        self.data = cls
        return cls

# create a data processor object to load and process the data
data_processor = DataProcessor('cached_data')
data_processor.load()

# example: to view bus stops data
bus_stops = data_processor.data['bus_stops']
# print(bus_stops)

# process data --> csv
# ura_data_1 = data_processor.data["ura_data"][1]["Result"]
# ura_data_2 = data_processor.data["ura_data"][2]["Result"]
# #ura_data_3 = data_processor.data["ura_data"][3]["Result"]   # FOR SOME REASON, BATCH 3 IS GIVING PROBLEMS. Comment it out...
# ura_data_4 = data_processor.data["ura_data"][4]["Result"]
# ura_1 = pd.DataFrame.from_dict(ura_data_1)
# ura_2 = pd.DataFrame.from_dict(ura_data_2)
# #ura_3 = pd.DataFrame.from_dict(ura_data_3)                  # FOR SOME REASON, BATCH 3 IS GIVING PROBLEMS. Comment it out...
# ura_4 = pd.DataFrame.from_dict(ura_data_4)
# ura = pd.concat([ura_1,ura_2,
#                  #ura_3,                                     # FOR SOME REASON, BATCH 3 IS GIVING PROBLEMS. Comment it out...
#                  ura_4])
# ura.to_csv("ura_unconverted.csv")

# process data other than the URA private residential property transaction data

bus_stops = data_processor.data['bus_stops']['value']
taxi_stands=data_processor.data['taxi_stands']['value']
carparks=data_processor.data['carpark_availability']['value']
#train_stations=data_processor.data['geospatial']['TrainStation']
#cycling_paths=data_processor.data['geospatial']['CyclingPath']
# train_station_exits=data_processor.data['geospatial']['TrainStationExit']
# school_zones=data_processor.data['geospatial']['SchoolZone']


df_bus_stops = pd.DataFrame.from_dict(bus_stops)
df_taxi_stands = pd.DataFrame.from_dict(taxi_stands)
df_carparks = pd.DataFrame.from_dict(carparks)
df_carparks[['latitude', 'longitude']] = df_carparks['Location'].str.split(' ', 1, expand=True)

df_bus_stops.to_csv("./data/bus_stops.csv")
df_taxi_stands.to_csv("./data/taxi_stands.csv")
df_carparks.to_csv("./data/carparks.csv")