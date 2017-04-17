import pandas as pd
import json

in_file = "profiles0_scraped.txt"

df = pd.DataFrame()
chunk = pd.DataFrame()
chunk_size = 1000
i = 0

with open(in_file) as f:
    for line in f.readlines():

        try:
            json_line = json.loads(line)
        except:
            print("json error")
            continue

        user = {'profile': json_line['profile']}

        for game in json_line['games']:
            user["appid" + str(game['appid'])] = 1

        user_df = pd.DataFrame(user, index=[user['profile']])
        chunk = pd.concat([chunk, user_df])

        # series = pd.Series(user.values(), user.keys())
        # chunk = pd.concat([chunk, series])

        print(i)
        i += 1
        if i >= chunk_size:
            df = pd.concat([df, chunk])
            chunk = pd.DataFrame()
            i = 0

    df = pd.concat([df, chunk])
    df.to_csv(in_file.strip(".txt") + "_csv.csv")
