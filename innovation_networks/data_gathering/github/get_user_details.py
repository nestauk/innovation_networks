"""Using a list of GitHub user dictionaries, get further details e.g.
followers, repos, organisations"""

import argparse
import json
import logging
import os
import ratelim
import requests
import sys
import time

from datetime import datetime


def details_url(login, detail_type):
    """Construct a GitHub API compliant API for a user and
    detail type"""
    url = ('https://api.github.com/users/' +
           '{}/'.format(login) +
           '{}'.format(detail_type))
    return url


@ratelim.patient(5000, 3600)
def request_details(login, detail_type='repos', auth=None):
    """GET request to api.github for user and detail type. Optionally
    authenticate for higher rate limits"""
    url = details_url(login, detail_type)
    if not auth:
        req = requests.get(url)
    else:
        req = requests.get(url,
                           auth=auth)
    return req


def get_file_path():
    """Get the path to the current file"""
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def out_file_name(out_path, detail_type):
    """Formatted file name"""
    file_name = '{}_github_uk_user_{}.json'.format(
        datetime.now().strftime("%Y%m%d%H"), detail_type)
    return os.path.join(out_path, file_name)


def username_passw():
    """Get GitHub username and password from the user's environment"""
    try:
        auth = (os.environ['GH_USERN'], os.environ['GH_PASSW'])
    except KeyError:
        raise KeyError("No username or password found in the environment. Please set " +
                       "these and try again")
        auth = None
    return auth


def request_rate_limit_remaining(auth_details=None):
    """Check the remaining GitHub API calls remaining, returning the
    response object. Optionally authenticate with a username and password tuple
    to check against you login's remaining rate limit"""
    if not auth_details:
        r = requests.get('https://api.github.com/rate_limit').json()
    else:
        r = requests.get('https://api.github.com/rate_limit',
                         auth=(auth_details[0],
                               auth_details[1])).json()
    return r


def returned_rate_limit_remaining(returned_request):
    """the remaining number of calls from a GitHub response object
    using the response's headers. Returns an integer value"""
    return int(returned_request.headers.get('x-ratelimit-remaining'))


def rate_limit_ok(auth_details=None):
    """Check whether any calls are remaining. If there are, return True, else
    wait until the limit is refreshed and then return True."""
    if not auth_details:
        r = request_rate_limit_remaining()
    else:
        r = request_rate_limit_remaining(auth_details)

    remaining = r.get('resources', {}).get('core', {}).get('remaining', 0)
    if remaining > 0:
        return True
    else:
        time_till_renewal = r.get('resources', {}).get('core', {}).get('reset', None)
        delta = datetime.fromtimestamp(time_till_renewal) - datetime.now()
        print('Waiting until {}'.format(
            datetime.fromtimestamp(time_till_renewal)))
        time.sleep(delta.seconds)


def main():
    """Main function"""
    logging.basicConfig(level=logging.DEBUG,
                        filename='/tmp/github.user_details.log')

    parser = argparse.ArgumentParser(description="Get details on GitHub Users")

    parser.add_argument(dest='datafile',
                        action='store',
                        help='path to data file')

    parser.add_argument(dest='outpath',
                        action='store',
                        help='path to out directory')

    args = parser.parse_args()

    auth_details = (username_passw())

    # make the path if it doesn't exist
    if not os.path.exists(args.outpath):
        os.mkdir(args.outpath)

    with open(args.datafile, 'r') as fp:
        data = json.load(fp)

    detail_types = ['repos']
    for detail_type in detail_types:
        out_file = out_file_name(args.outpath, detail_type)
        for user in data[:2]:
            login = user.get('user')
            if rate_limit_ok(auth_details):
                r = request_details(login, detail_type=detail_type, auth=auth_details)
                rate_remaining = returned_rate_limit_remaining(r)
                if rate_remaining > 0:
                    continue
                else:
                    rate_limit_ok(auth_details)


if __name__ == "__main__":
    main()
