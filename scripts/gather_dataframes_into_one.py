import glob
import pandas as pd
import json

df = pd.DataFrame()

print(glob.glob('./**/*.csv'))

for file in glob.glob('./**/*.csv'):
    if "_dataframe_merged.csv" not in file:
        print("concatenating file:", file)
        chunk = pd.read_csv(file, index_col=0)
        df = pd.concat([df, chunk])

df.to_csv("wip_data\\_dataframe_merged.csv")

appids = []

for index, _ in df.iteritems():
    if "appid" in index:
        appids.append(index)

with open("wip_data\\_dataframe_merged_appids.txt", 'w') as f:
    f.write(json.dumps(appids))