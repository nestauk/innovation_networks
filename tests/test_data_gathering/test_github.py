import pytest

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
