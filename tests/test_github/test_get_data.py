import json
import logging
import os
import responses

from datetime import datetime, timedelta
from innovation_networks.data_gathering.github import get_data


def test_make_url():
    """GitHub Archive URL creation works"""
    day = 6
    year = 1987
    month = 11
    hour = 8
    url = get_data.make_url(year=year,
                            month=month,
                            day=day,
                            hour=hour)
    test_url = "http://data.githubarchive.org/1987-11-06-08.json.gz"
    assert url == test_url


def test_urls():
    """Correct urls are returned for two year period"""
    urls_list = get_data.urls()
    test_url = ("http://data.githubarchive.org/{}.json.gz"
                .format((datetime.now() - timedelta(731)).strftime("%Y-%m-%d-%H")))
    assert len(urls_list) == 731
    assert urls_list[0] == test_url


def test_daterange():
    """dateranges are correct"""
    l = (datetime(2016, 6, 6, 0, 0),
         datetime(2016, 6, 7, 0, 0))
    x = get_data.daterange(start_date=datetime(2016, 6, 6),
                           end_date=datetime(2016, 6, 8))
    assert l == tuple(x)


def test_filename():
    """Filenames are correct format"""
    t = "{}".format('{}_github_event_data.json.gz'.format(
        datetime.now().strftime("%Y%m%d%S")))
    assert t == get_data.out_file_name('~/').split('/')[-1:][0]


@responses.activate
def test_write_data():
    """Test wrting data works"""
    responses.add(responses.GET, 'http://test.com',
                  body='{"test": "test data"}',
                  content_type='application/json')
    fp = open('.temp', 'wb')
    url_list = ["http://test.com"]
    get_data.write_data(fp, url_list)
    fp.close()
    with open('.temp', 'r') as fp:
        d = json.load(fp)
    assert d == json.loads('{"test": "test data"}')
    os.remove('.temp')
