import json
import pandas as pd
import numpy as np
from scripts import encoder

"""
GraphBuilder gathers previously scrapped data from main json file,
and returns a proximity matrix or networkx graph.
"""
class GraphBuilder:

    def __init__(self,
                 json_master_path="\\wip_data\\users_master.json"):
        self.json_master_path = json_master_path
        self.graph = None

    def gather_data(self):
        pass

    def get_graph(self):

        with open(self.json_master_path) as f:
            json_users = json.load(f)

        df = self._build_users_df(json_users)

        return self.graph

    """Returns a DataFrame, in which games are columns, and users are in rows.
    
    Values of cells are 0 if user doesn't have the game, or 1 if they do.
    
    Args:
        json_users - JSON object containing all users.
    """
    def _build_users_df(self, json_users) -> pd.DataFrame:

        i = 0
        series_list = []
        for user in json_users:
            games_arr = GraphBuilder._get_games_array(user)
            if not games_arr:
                continue
            values = [1 for _ in games_arr]
            series = pd.Series(data=values, index=games_arr, dtype=np.int8)
            series.name = GraphBuilder._get_user_name(user)
            series_list.append(series)

            if i % 100 == 0:
                print(i)
            i += 1

        df = pd.concat(series_list, axis=1).T.fillna(0).astype(np.int8)
        return df

    """Trims a dataframe to a minimal size.
     
    Given that the source dataframe might be hundred thousands or even 
    millions entries long, not all of these users give new meaningful
    information about relationships between games. Thus, this method
    aims to remove as much users as possible, but still leave enough
    so that every game could have a sizable and diverse users pool.
    
    Args:
        min_users (int) - minimal amount of users each game should
            have, if able.
    """
    def _trim_users_dataframe(self, df, min_users=50):
        pass

    @staticmethod
    def _get_games_array(user) -> list:

        try:
            games_str = user['g']
        except KeyError:
            print('user jsonobject has no games key: ', user)
            return []

        if games_str == "" or games_str == "error":
            return []

        games_arr = encoder.Encoder().decode_user_games_alpha(games_str)
        return games_arr

    @staticmethod
    def _get_user_name(user) -> string:
        try:
            return user['p']
        except KeyError:
            return 'NoName'

