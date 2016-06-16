"""Search the parsed users data for users at a location"""

import argparse
import json
import logging
import re


def main():
    """Main function"""
    logging.basicConfig(filename='/tmp/github.users_at_location.log',
                        level=logging.ERROR,
                        format='%(levelname)s:%(asctime)s,%(message)s')

    # Parser for command line arguments
    parser = argparse.ArgumentParser(description=("Filter the github " +
                                                  "user data by location"))

    # place names filename
    parser.add_argument(dest='place_names',
                        action='store',
                        help='file containing placenames, 1 per line')

    # input filename
    parser.add_argument(dest='datafile',
                        action='store',
                        help='file containing github user data')

    # Output filename
    parser.add_argument(dest='outfile',
                        action='store',
                        help='output filename for storing data')

    args = parser.parse_args()

    # This can cause memory issues on low memory systems
    # Either up the memory or amend to use a streaming JSON library
    with open(args.datafile, 'r') as fp:
        data = json.load(fp)

    # List of towns and cities
    with open(args.place_names, 'r') as fp:
        towns_and_cities = fp.read().splitlines()

    # List of entries that have a 'location' key
    data_locations = [x for x in data if 'location' in x['attributes']]

    # Check against UK towns and cities
    data_uk_locations = []
    for x in data_locations:
        words = x['attributes']['location'].lower().split()
        for word in words:
            if word in towns_and_cities:
                data_uk_locations.append(x)

    # Remove some errors due to similar placenames
    # Mostly US places (New York matches York, Cambridge, MA matches Cambridge)
    new_york = re.compile(r'new york')
    final_locations = [x for x in data_uk_locations if not new_york.findall(x['attributes']['location'].lower())]
    final_locations = [x for x in final_locations if x['attributes']['location'].lower() not in error_names]

    with open(args.outfile, 'w') as fp:
        json.dump(final_locations, fp)


if __name__ == "__main__":
    main()
