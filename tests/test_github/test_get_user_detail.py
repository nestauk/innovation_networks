import json
import pytest
import responses

from datetime import datetime
from innovation_networks.data_gathering.github import get_user_details


def test_details_url():
    """Test API query URLs are correctly formatted"""
    url = get_user_details.details_url("james", 'repos')
    comparison = "https://api.github.com/users/james/repos"
    assert url == comparison


@responses.activate
def test_request_details_no_auth():
    """Test correct request being issued to GitHub API"""
    responses.add(responses.GET,
                  'https://api.github.com/users/james/repos',
                  body='{"valid": "response"}')

    resp = get_user_details.request_details('james', 'repos')
    assert resp.json() == {'valid': 'response'}
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'https://api.github.com/users/james/repos'
    assert responses.calls[0].response.text == '{"valid": "response"}'


def test_out_file_name():
    """Test file name is formatted correctly. Could break if hour changes
    during test"""
    now = datetime.now().strftime("%Y%m%d%H")

    file_name = '{}_github_uk_user_{}.json'.format(
        now,
        'repos'
    )

    assert file_name == get_user_details.out_file_name('./', 'repos').split('/')[-1:][0]


def test_username_passw(monkeypatch):
    """Test that the tuple containing username and password is correctly returned"""
    monkeypatch.setenv('GH_USERN', 'user')
    monkeypatch.setenv('GH_PASSW', 'passw')
    auth_tuple = get_user_details.username_passw()

    assert auth_tuple == ('user', 'passw')


def test_username_passw_no_variables(monkeypatch):
    """Test that the correct error is raised and recovered from when the GH
    username and password aren't set as environment variables"""
    with pytest.raises(KeyError):
        monkeypatch.delenv('GH_USERN')
        monkeypatch.delenv('GH_PASSW')
        auth_tuple = get_user_details.username_passw()


def test_username_passw_one_variable(monkeypatch):
    """Test that the correct error is raised and recovered from when the GH
    username and password aren't set as environment variables"""
    with pytest.raises(KeyError):
        monkeypatch.delenv('GH_USERN')

        get_user_details.username_passw()


@responses.activate
def test_request_rate_limit_remaining():
    """Test rate limits are working correctly when not authorised"""
    responses.add(responses.GET,
                  'https://api.github.com/rate_limit',
                  body='{"valid": "response"}')
    resp = get_user_details.request_rate_limit_remaining()

    assert resp == {'valid': 'response'}
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'https://api.github.com/rate_limit'
    assert responses.calls[0].response.text == '{"valid": "response"}'


@responses.activate
def test_request_rate_limit_remaining_authd():
    """Test rate limits are working correctly when authorised"""
    responses.add(responses.GET,
                  'https://api.github.com/rate_limit',
                  body='{"valid": "response"}')

    resp = get_user_details.request_rate_limit_remaining(auth_details=('user', 'passw'))

    assert resp == {'valid': 'response'}
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'https://api.github.com/rate_limit'
    assert responses.calls[0].response.text == '{"valid": "response"}'


@responses.activate
def test_returned_rate_limit_remaining():
    """Test headers containing rate limits are properly read"""
    def request_callback(request):
        resp_body = {'valid': 'response'}
        headers = {'x-ratelimit-remaining': '5'}
        return (200, headers, json.dumps(resp_body))

    responses.add_callback(
        responses.GET, 'https://api.github.com/users/james/repos',
        callback=request_callback,
        content_type='application/json',
    )

    resp = get_user_details.request_details('james', 'repos')
    remaining = get_user_details.returned_rate_limit_remaining(resp)

    assert remaining == 5


@responses.activate
def test_rate_limit_ok_not_authd():
    """Test that rate limits are correctly checked"""
    def request_callback(request):
        resp_body = {'resources': {'core': {'remaining': 5}}}
        headers = {'x-ratelimit-remaining': '5'}
        return (200, headers, json.dumps(resp_body))

    responses.add_callback(
        responses.GET, 'https://api.github.com/rate_limit',
        callback=request_callback,
        content_type='application/json',
    )

    resp = get_user_details.rate_limit_ok()

    assert resp == True
