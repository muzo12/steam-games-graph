import pandas as pd
import json

# users' libraries scraped with scrap_from_profiles.py
in_files = ["wip_data\\profiles" + str(i) + "_scraped.txt" for i in range(0, 1)]

def concatenate_df(_chunk):
    #print("concatenating dataframe...")
    global df
    df = pd.concat([df, _chunk])
    global chunk
    chunk = pd.DataFrame()
    print(str(df.shape[0]/f_len*100)+"%", "dataframe concatenated, shape:", df.shape)

for in_file in in_files:

    df = pd.DataFrame()
    chunk = pd.DataFrame()
    chunk_size = 250  # dividing data into chunks before concatenating into final dataframe works better
    i = 0
    games_meta = {}

    # calculate file length
    with open(in_file) as f:

        for i, l in enumerate(f):
            pass
        f_len = i+1
        print("reading file:", in_file, "file length:",f_len,"chunk size:", chunk_size)

    with open(in_file) as f:

        for line in f.readlines():

            try:
                json_line = json.loads(line)
            except:
                print("json error")
                continue

            # 'profile' column is unnecessary? it's in index anyway
            if 'time' in list(json_line.keys()):
                user = {'profile': json_line['profile'], 'time': json_line['time']}
            else:
                user = {'profile': json_line['profile']}

            for game in json_line['games']:
                if game['appid'] not in list(games_meta.keys()):
                    games_meta[game['appid']] = {'number': 1, 'user': json_line['profile'], 'total_playtime': game['playtime_forever']}
                else:
                    games_meta[game['appid']]['number'] += 1
                    games_meta[game['appid']]['total_playtime'] += game['playtime_forever']
                user["appid" + str(game['appid'])] = 1

            user_df = pd.DataFrame(user, index=[user['profile']])
            chunk = pd.concat([chunk, user_df])

            #print(i)
            i += 1
            if i >= chunk_size:
                concatenate_df(chunk)
                i = 0

        concatenate_df(chunk)
        print("saving csv")
        df.to_csv(in_file.strip(".txt") + "_csv.csv")
        print("saving meta")
        with open(in_file.strip(".txt") + "_meta.txt", 'w') as meta_f:
            meta_f.write(json.dumps(games_meta))
