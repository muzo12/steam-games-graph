import os.path
import json
import random


class TestUserFileCreator:
    pass

if __name__ == '__main__':
    json_master_path = "/wip_data/users_master.json"
    json_master_path = os.path.dirname(__file__) + json_master_path
    test_file_path = "/test_users_master.json"
    test_file_path = os.path.dirname(__file__) + test_file_path
    number_of_users = 25000

    with open(json_master_path, 'r') as f:
        json_users = json.load(f)

    random.shuffle(json_users)
    test_users = json_users[:number_of_users]

    with open(test_file_path, 'w+') as f:
        json.dump(test_users, f, indent=2)

    print("Successfully created test_users_master.json file with {} users"
          .format(number_of_users))
