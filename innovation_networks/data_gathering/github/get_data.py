"""Get GitHub data for the innovation networks data pilot.
Uses https://www.githubarchive.org/ and gets the last 2 years of
activity"""

import calendar
import logging
import os
import requests
import sys

from collections import deque
from datetime import datetime, timedelta
from time import sleep


def get_file_path():
    """Get the path to the current file"""
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def make_url(date_stamp=None,
             year=datetime.now().year,
             month=datetime.now().month,
             day=datetime.now().day - 1,
             hour=datetime.now().hour):
    """Return a GitHub Archive URL that will get data for
    the given year and month. Defaults to the current hour for yesterday."""
    base_url = "http://data.githubarchive.org/"
    if date_stamp:
        return base_url + date_stamp + '.json.gz'
    else:
        return (base_url +
                str(year) + '-' +
                '{:02d}'.format(month) + '-' +
                '{:02d}'.format(day) + '-' +
                '{:02d}'.format(hour) + '.json.gz')


def urls():
    """Returns a list of formatted GitHubArchive URLs"""
    return [make_url(single_date.strftime("%Y-%m-%d-%H")) for
            single_date in daterange()]


def daterange(start_date=datetime.now() - timedelta(2),
              end_date=datetime.now()):
    """yields dates for last two years, counting from yesterday"""
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def out_file_name(out_path):
    """Formatted file name"""
    file_name = '{}_github_event_data.json.gz'.format(
        datetime.now().strftime("%Y%m%d%S"))
    return os.path.join(out_path, file_name)


def write_data(file_obj, url_list):
    """Iterate through url_list, use requests to stream the file,
    writing to disk in chunks"""
    for url in url_list:
        req = requests.get(url, stream=True)
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                file_obj.write(chunk)
        file_obj.flush()
        del(url_list[0])
        sleep(2)


def main():
    logging.basicConfig(level=logging.DEBUG, filename='/tmp/github.get_data.log')

    # Set the cwd to this file's
    os.chdir(get_file_path())

    # All the urls for the json data as a deque object
    # that supports left sided pop
    url_list = urls()
    # Standard data folder
    out_path = "../../data/"

    # make the path if it doesn't exist
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    out_file = out_file_name(out_path)

    try:
        fp = open(out_file, 'wb')
        write_data(fp, url_list)
        fp.close()
    except Exception as e:
        logging.error(e, exc_info=True)
        wait(10)
        # Restart, the list will still hold the relevant url,
        # as the 0 index isn't deleted until after file is flushed
        write_data(fp, url_list)

if __name__ == "__main__":
    main()
