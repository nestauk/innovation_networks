"""Parse the GitHub event stream data for unique User IDs"""

import argparse
import json
import logging
import os

from datetime import datetime
from .get_data import get_file_path
from sys import stdout

def out_file_name(out_path):
    """Formatted file name"""
    file_name = '{}_github_event_data_usernames.json'.format(
        datetime.now().strftime("%Y%m%d%H"))
    return os.path.join(out_path, file_name)


def make_user_list(datafile):
    # List of usernames that we will need to gather data on
    users = []
    # Parse the data file for usernames
    with open(datafile, 'r') as fp:
        # Used for printing number of users parsed
        x = 1

        for line in fp:
            # Except block, incase of non-compliant JSON
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                data = {}
                logging.error(e)
            if 'actor' in data:
                if "actor_attributes" in data:
                    out_data = {'user': data['actor'],
                                'attributes': data['actor_attributes']}
                else:
                    out_data = {'user': data['actor']['login'],
                                'attributes': data['actor']}
                users.append(out_data)
            elif "login" in data.get("sender", {}):
                users.append(data["sender"]["login"])
            print('Parsed {} GitHub Events'.format(x), end='\r')
            x += 1
            stdout.flush()
    print("\nAll users processed")
    return users


def main():
    logging.basicConfig(filename='/tmp/github.parse_users.log',
                        level=logging.ERROR,
                        format='%(levelname)s:%(asctime)s,%(message)s')

    # Parser for command line arguments
    parser = argparse.ArgumentParser(description=("Parse GitHub Event data" +
                                                  "for users"))

    # input filename
    parser.add_argument(dest='datafile',
                        action='store',
                        help='file containing github event data')

    # output path
    parser.add_argument(dest='outpath',
                        action='store',
                        help='path to output directory')

    # Store it in args
    args = parser.parse_args()

    # Set the cwd to this file's
    os.chdir(get_file_path())

    # Standard data folder
    out_path = args.outpath

    # make the path if it doesn't exist
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    # Make the output file
    outfile = out_file_name(out_path)

    # List of usernames andtheir attributes
    user_list = make_user_list(args.datafile)

    # Write to file
    with open(outfile, 'w') as fp:
        json.dump(user_list, fp)

if __name__ == "__main__":
    main()
