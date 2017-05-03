import pandas as pd
import json

# users' libraries scraped with scrap_from_profiles.py
in_files = ["wip_data\\profiles" + str(i) + "_scraped.txt" for i in range(40, 41)]

#redirects file
with open("wip_data\\_redirects_from_to.json", 'r') as f:
    redirects = json.loads(f.read())

for in_file in in_files:

    df = pd.DataFrame()
    small_chunk = pd.DataFrame()
    large_chunk = pd.DataFrame()
    small_chunk_tresh = 250  # dividing data into chunks before concatenating into final dataframe works better
    large_chunk_tresh = 5000

    games_meta = {}

    # calculate file length
    with open(in_file) as f:

        for i, l in enumerate(f):
            pass
        f_len = i+1
        print("reading file:", in_file, "file length:", f_len,
              "small chunk size:", small_chunk_tresh, "large chunk size:", large_chunk_tresh)

    with open(in_file) as f:
        i = 0
        print('starting...')

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

            games_to_remove = []     # we'll use that after first iteration
            for game in json_line['games'][:]:  # first iteration, manage redirects. iterate over a shallow copy.
                if str(game['appid']) in list(redirects.keys()):
                    #print('redirect!',game)
                    new_appid = redirects[str(game['appid'])]
                    #print('looking for:',new_appid)

                    new_gamedict = {}
                    for q_game in json_line['games']:
                        if q_game['appid'] == new_appid:
                            new_gamedict = q_game
                    #print(new_gamedict)
                    if new_gamedict == {}:
                        json_line['games'].append(new_gamedict) # this might cause problems (shouldn't on shallow copy)

                    if 'appid' not in list(new_gamedict.keys()):
                        new_gamedict['appid'] = new_appid
                    if 'playtime_forever' not in list(new_gamedict.keys()):
                        new_gamedict['playtime_forever'] = game['playtime_forever']
                    else:
                        new_gamedict['playtime_forever'] += game['playtime_forever']
                    #print('final gamedict:',new_gamedict,'\n')

                    games_to_remove.append(game)

            for game in games_to_remove:
                json_line['games'].remove(game)

            for game in json_line['games']: #second iteration, do actual dataframe and meta stuff
                if str(game['appid']) in list(redirects.keys()):
                    print('!!! still problems! !!!')
                if game['appid'] not in list(games_meta.keys()):
                    games_meta[game['appid']] = {'number': 1, 'user': json_line['profile'], 'total_playtime': game['playtime_forever']}
                else:
                    games_meta[game['appid']]['number'] += 1
                    games_meta[game['appid']]['total_playtime'] += game['playtime_forever']
                user["appid" + str(game['appid'])] = 1

            user_df = pd.DataFrame(user, index=[user['profile']])
            small_chunk = pd.concat([small_chunk, user_df])

            i += 1

            if small_chunk.shape[0] >= small_chunk_tresh:
                large_chunk = pd.concat([large_chunk, small_chunk])
                print("progress: %.2f" % (i * 100 / f_len) + "%",
                      "| small_chunk concatenated, large_chunk:", large_chunk.shape)
                small_chunk = pd.DataFrame()

            if large_chunk.shape[0] >= large_chunk_tresh:
                df = pd.concat([df, large_chunk])
                print("large_chunk concatenated, df:", df.shape)
                large_chunk = pd.DataFrame()

        print("finalizing...")
        large_chunk = pd.concat([large_chunk, small_chunk])
        print("progress: %.2f" % (i * 100 / f_len) + "%",
              "| small_chunk concatenated, large_chunk:", large_chunk.shape)
        df = pd.concat([df, large_chunk])
        print("large_chunk concatenated, df:", df.shape)

        print("saving csv")
        df.to_csv(in_file.strip(".txt") + "_redirects_csv.csv")
        print("saving meta")
        with open(in_file.strip(".txt") + "_redirects_meta.txt", 'w') as meta_f:
            meta_f.write(json.dumps(games_meta))
        print("finished!")