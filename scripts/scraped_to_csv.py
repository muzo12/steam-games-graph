import pandas as pd
import json

in_file = "profiles0_scraped.txt"       # users' libraries scraped with scrap_from_profiles.py

df = pd.DataFrame()
chunk = pd.DataFrame()
chunk_size = 1000  # dividing data into chunks before concatenating into final dataframe works better
i = 0

def concatenate_df(_chunk):
    print("contatenating dataframe...")
    global df
    df = pd.concat([df, _chunk])
    global chunk
    chunk = pd.DataFrame()
    print("dataframe concatenated, shape:", df.shape)


with open(in_file) as f:
    for line in f.readlines():

        try:
            json_line = json.loads(line)
        except:
            print("json error")
            continue

        user = {'profile': json_line['profile']}        # 'profile' column is unnecessary? it's in index anyway

        for game in json_line['games']:
            user["appid" + str(game['appid'])] = 1

        user_df = pd.DataFrame(user, index=[user['profile']])
        chunk = pd.concat([chunk, user_df])

        print(i)
        i += 1
        if i >= chunk_size:
            concatenate_df(chunk)
            i = 0

    concatenate_df(chunk)
    print("saving csv")
    df.to_csv(in_file.strip(".txt") + "_csv.csv")
