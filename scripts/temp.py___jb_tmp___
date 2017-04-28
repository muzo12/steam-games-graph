import pandas as pd
import json

df = pd.read_csv("wip_data\\_dataframe_merged.csv", index_col=0)

appids = []

for index, _ in df.iteritems():
    if "appid" in index:
        appids.append(index)

with open("_dataframe_merged_appids.txt", 'w') as f:
    f.write(json.dumps(appids))