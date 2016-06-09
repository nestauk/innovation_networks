import pytest

from datetime import datetime, timedelta
from innovation_networks.data_gathering.github import get_data, urls


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
    urls_list = urls()
    test_url = ("http://data.githubarchive.org/{}.json.gz"
                .format((datetime.now() - timedelta(731)).strftime("%Y-%m-%d")))

    assert len(urls_list) == 731
    assert urls_list[0] == test_url
