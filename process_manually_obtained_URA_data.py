from SVY21 import SVY21
import json
import pandas as pd

# https://stackoverflow.com/questions/1518522/find-the-most-common-element-in-a-list
from collections import Counter
def most_common(lst):
    data = Counter(lst)
    return data.most_common(1)[0][0]

#######################

batch1_json = open("./data/batch1.json", 'r')
batch1 = json.load(batch1_json)

batch2_json = open("./data/batch2.json", 'r')
batch2 = json.load(batch2_json)

#batch3_json = open("./ura_data/batch2.json",'r') ## Batch 3 is the problematic batch
#batch3 = json.load(batch3_json) ## Batch 3 is the problematic batch

batch4_json = open("data/batch4.json", 'r')
batch4 = json.load(batch4_json)

data = batch1['Result']+batch2['Result']+batch4['Result'] #+batch3['Result'] ## Batch 3 is the problematic batch

print('Number of properties',len(data)) #________

properties_with_SVY21_coordinates = [property for property in data if 'x' in property.keys() and 'y' in property.keys()]

print('Number of properties with coordinates',len(properties_with_SVY21_coordinates)) #________

coordinate_transformer = SVY21()

for property in properties_with_SVY21_coordinates:

    # Convert SVY21 coordinates into latitude and longitude
    x,y = float(property['x']),float(property['y'])
    lat,long = coordinate_transformer.computeLatLon(x, y)
    del property['x']
    del property['y']
    property['lat']=lat
    property['long']=long

    # Calculate avg price per sqm
    transactions = property['transaction']
    num_transactions = len(transactions)
    price_per_sqm = list(map(lambda transac: float(transac['price']) / float(transac['area']), transactions))
    avg_price_per_sqm = sum(price_per_sqm)/len(price_per_sqm)
    property['avg_price_per_sqm'] = avg_price_per_sqm

    # Get district
    district_list = map(lambda transac:transac['district'],transactions)
    district = most_common(district_list)
    property['district'] = district

    # Get commonest tenure
    tenure_list = map(lambda transac: transac['tenure'], transactions)
    tenure = most_common(tenure_list)
    property['commonest_tenure'] = tenure

    del property['transaction']

df = pd.DataFrame.from_dict(properties_with_SVY21_coordinates)
df.to_csv("./data/ura.csv")