import os
import requests
import json
import time
from scripts import Encoder


class ProfileScrapper():

    format = "%y%m%d%H%M"

    def __init__(self,
                 json_master_path = "C:\\Users\\Admin\\Documents\\GitHub\\GamesGraph\\scripts\\wip_data\\users_master.json",
                 private_variables_path = "C:\\Users\\Admin\\Documents\\GitHub\\GamesGraph\\scripts\\private_variables.txt",
                 daily_limit=99000,
                 verbose=1):

        self.verbose = verbose
        self.json_master_path = json_master_path
        self.last_bak_file = None

        with open(private_variables_path) as var_f:
            for line in var_f.readlines():
                if line[0] == '#': continue
                if ("steam_api_key") in line:
                    steam_api_key = line.partition("steam_api_key=")[2]
                    steam_api_key = steam_api_key.strip("\n")
                    self.p("steam_api_key", steam_api_key)
                    self.steam_api_key = steam_api_key

        assert self.steam_api_key is not None

        self.daily_limit = daily_limit

        encoder = Encoder(alphabet="0123456789a")
        self.encoder = encoder


    def scrap(self):

        self.p("Reading json file")

        with open(self.json_master_path) as f:
            j = json.load(f)

        # self.p("Number of users:", len(j))
        self.p("Saving backup file")

        bak_file = self.json_master_path + "_bak_" + time.strftime("%y%m%d%H%M")
        with open(bak_file, 'w+') as f:
            json.dump(j, f)
        self.last_bak_file = bak_file

        self.p("Sorting profiles")

        j_sorted = sorted(j, key=lambda user: self.get_date(user))

        self.p("Sorting profiles finished")

        self.show_metrics(j_sorted)

        max_idx = min(len(j), self.daily_limit)

        self.p("Scrapping started")

        for idx in range(max_idx):
            if idx % 100 == 0:
                self.p("Progress: {:.3}%".format(idx / max_idx * 100))
            if idx % 1000 == 0 and idx > 0:
                self.p("Saving backup")
                bak_file = self.json_master_path + "_bak_wip_" + time.strftime(
                    "%y%m%d%H%M")

                with open(bak_file, 'w+') as f:
                    json.dump(j_sorted, f)

                if self.last_bak_file is not None and self.last_bak_file != bak_file:
                    os.remove(self.last_bak_file)

                self.last_bak_file = bak_file

            user = j_sorted[idx]
            try:
                self._scrap_user(user)
            except json.JSONDecodeError:
                self.p("{}: SCRAPING FAILED FOR USER: {}".format(idx, user['p']))
            time.sleep(0.1)

        with open(self.json_master_path, 'w') as f:
            json.dump(j_sorted, f, indent=2)

        if self.last_bak_file is not None:
            os.remove(self.last_bak_file)

    def _scrap_user(self, user):
        request = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=' + \
                  self.steam_api_key + '&steamid=' + user['p'] + '&format=json'
        response = requests.get(request)
        user['d'] = time.strftime(ProfileScrapper.format)

        try:
            json_response = json.loads(response.text)
        except:
            user['g'] = 'error'
            return

        if 'games' not in json_response['response']:
            user['g'] = 'error'
            return

        games_json = json_response['response']['games']
        games = [(game['appid']) for game in games_json]
        games_str = self.encoder.encode_games_array(games)

        user['g'] = games_str

    def p(self, *msg):
        if self.verbose:
            txt = ""
            for m in msg:
                txt += m + ", "
            t = time.strftime("%H:%M")
            print("SCRAPPER\t" + t + "\t", txt[:-2])

    def show_metrics(self, j_sorted):

        num_errors = 0
        num_empty = 0
        min_date = time.strptime('6012302323', ProfileScrapper.format)

        for user in j_sorted:
            try:
                if user['g'] == 'error':
                    num_errors += 1
                elif user['g'] == '':
                    num_empty += 1
            except KeyError:
                num_empty += 1

            date = ProfileScrapper.get_date(user)
            if date < min_date:
                min_date = date

        self.p("Number of users:\t{}".format(len(j_sorted)))
        correct_users = len(j_sorted) - num_empty
        self.p("Scrapped users:\t{}\t({:.3}%)".format(correct_users,
                                                 correct_users/len(j_sorted) * 100))
        self.p("Errorenous users:\t{}\t({:.3}%)".format(num_errors,
                                                   num_errors/correct_users * 100))
        self.p("Correct users:\t{}".format(correct_users - num_errors))
        self.p("Earliest date: {}".format(min_date))

    @staticmethod
    def get_date(user):
        try:
            date = time.strptime(user['d'], ProfileScrapper.format)
        except KeyError:
            date = time.strptime('0001010000', ProfileScrapper.format)
        return date

if __name__ == '__main__':
    ProfileScrapper().scrap()
