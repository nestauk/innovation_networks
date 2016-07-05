#!/usr/bin/env/python
"""Script for getting repo details from github using the dict produced
by get_user_details.py"""

from get_user_details import get_file_path
from get_user_details import get_file_path, username_passw
from get_user_details import request_rate_limit_remaining, returned_rate_limit_remaining
from get_user_details import rate_limit_ok
from datetime import datetime

import argparse
import json
import logging
import os
import requests


def out_file_name(out_path):
    """Formatted file name"""
    file_name = '{}_github_uk_user_repo.json'.format(
        datetime.now().strftime("%Y%m%d%H"))
    return os.path.join(out_path, file_name)


def repos_url(login, repo_name):
    """Construct a GitHub API compliant API for a repo and
    """
    url = ('https://api.github.com/repos/' +
           '{}/'.format(login) +
           '{}'.format(repo_name))
    print(url)
    return url


def request_repo_details(login, repo_name, auth=None):
    """GET request to api.github for repo data. Optionally
    authenticate for higher rate limits"""
    url = repos_url(login, repo_name)
    if not auth:
        req = requests.get(url)
    else:
        req = requests.get(url, auth=auth)
    return req


def repo_crawl(data, auth_details=None, out_file=None):
    """Get more detailed data on repos"""
    with open(out_file, mode='w', encoding='utf-8') as fp:
        if rate_limit_ok(auth_details):
            for user in list(data.keys())[0:10]:
                print(user)
                repo_dict = {}
                repo_dict[user] = []
                for repo in data[user]:
                    print(repo)
                    repo_name = repo.get('name')
                    r = request_repo_details(user, repo_name, auth=auth_details)
                    repo_dict[user].append(r.json())
                    rate_remaining = returned_rate_limit_remaining(r)
                    if rate_remaining > 0:
                        continue
                    else:
                        rate_limit_ok(auth_details)
                json.dump(repo_dict, fp)


def main():
    """Main function for running as script"""
    logging.basicConfig(level=logging.DEBUG,
                        filename='/tmp/github.user_repos.log')

    parser = argparse.ArgumentParser(description="Get details on GitHub Users")

    parser.add_argument(dest='datafile',
                        action='store',
                        help='path to data file')

    parser.add_argument(dest='outpath',
                        action='store',
                        help='path to out directory')

    args = parser.parse_args()

    auth_details = (username_passw())

    # make the outpath if it doesn't exist
    if not os.path.exists(args.outpath):
        os.mkdir(args.outpath)

    # open the data file contianing login names
    with open(args.datafile, 'r') as fp:
        data = json.load(fp)

    repo_crawl(data, auth_details, out_file_name(args.outpath))

if __name__ == "__main__":
    main()
