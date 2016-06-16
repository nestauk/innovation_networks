import json
import logging
import sys

from datetime import datetime
from innovation_networks.data_gathering.github import parse_users


def test_filename():
    """Filenames are correct format"""
    t = "{}".format('{}_github_event_data_usernames.json'.format(
        datetime.now().strftime("%Y%m%d%H")))
    assert t == parse_users.out_file_name('~/').split('/')[-1:][0]


def test_make_user_list():
    """Correct json from user list"""
    json_str = '[{"user": "VarsosEmblem","attributes": {"login":"VarsosEmblem","type":"User","gravatar_id":"f3ff0eed4f3576ff340574e6fd381d8c","name":"Varsos","company":"juustoleipa","blog":"","location":"Silicon Valley, CA","email":"varsosemblem@gmail.com"}}]'
    test_json = json.loads(json_str)
    returned_json = parse_users.make_user_list('tests/test_github/test_user_data.json')
    assert test_json == returned_json
