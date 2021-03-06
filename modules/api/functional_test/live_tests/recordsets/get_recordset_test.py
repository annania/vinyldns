import pytest
import uuid

from utils import *
from hamcrest import *
from vinyldns_python import VinylDNSClient

def test_get_recordset_no_authorization(shared_zone_test_context):
    """
    Test getting a recordset without authorization
    """
    client = shared_zone_test_context.ok_vinyldns_client
    client.get_recordset(shared_zone_test_context.ok_zone['id'], '12345', sign_request=False, status=401)


def test_get_recordset(shared_zone_test_context):
    """
    Test getting a recordset
    """
    client = shared_zone_test_context.ok_vinyldns_client
    result_rs = None
    try:
        new_rs = {
            'zoneId': shared_zone_test_context.ok_zone['id'],
            'name': 'test_get_recordset',
            'type': 'A',
            'ttl': 100,
            'records': [
                {
                    'address': '10.1.1.1'
                },
                {
                    'address': '10.2.2.2'
                }
            ]
        }
        result = client.create_recordset(new_rs, status=202)
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']

        # Get the recordset we just made and verify
        result = client.get_recordset(result_rs['zoneId'], result_rs['id'])
        result_rs = result['recordSet']
        verify_recordset(result_rs, new_rs)

        records = [x['address'] for x in result_rs['records']]
        assert_that(records, has_length(2))
        assert_that('10.1.1.1', is_in(records))
        assert_that('10.2.2.2', is_in(records))
    finally:
        if result_rs:
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_get_recordset_zone_doesnt_exist(shared_zone_test_context):
    """
    Test getting a recordset in a zone that doesn't exist should return a 404
    """
    client = shared_zone_test_context.ok_vinyldns_client
    new_rs = {
        'zoneId': shared_zone_test_context.ok_zone['id'],
        'name': 'test_get_recordset_zone_doesnt_exist',
        'type': 'A',
        'ttl': 100,
        'records': [
            {
                'address': '10.1.1.1'
            },
            {
                'address': '10.2.2.2'
            }
        ]
    }
    result_rs = None
    try:
        result = client.create_recordset(new_rs, status=202)
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        client.get_recordset('5678', result_rs['id'], status=404)
    finally:
        if result_rs:
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_get_recordset_doesnt_exist(shared_zone_test_context):
    """
    Test getting a new recordset that doesn't exist should return a 404
    """
    client = shared_zone_test_context.ok_vinyldns_client
    client.get_recordset(shared_zone_test_context.ok_zone['id'], '123', status=404)


def test_at_get_recordset(shared_zone_test_context):
    """
    Test getting a recordset with name @
    """
    client = shared_zone_test_context.ok_vinyldns_client
    ok_zone = shared_zone_test_context.ok_zone
    result_rs = None
    try:
        new_rs = {
            'zoneId': ok_zone['id'],
            'name': '@',
            'type': 'TXT',
            'ttl': 100,
            'records': [
                {
                    'text': 'someText'
                }
            ]
        }
        result = client.create_recordset(new_rs, status=202)
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']

        # Get the recordset we just made and verify
        result = client.get_recordset(result_rs['zoneId'], result_rs['id'])
        result_rs = result['recordSet']

        expected_rs = new_rs
        expected_rs['name'] = ok_zone['name']
        verify_recordset(result_rs, expected_rs)

        records = result_rs['records']
        assert_that(records, has_length(1))
        assert_that(records[0]['text'], is_('someText'))

    finally:
        if result_rs:
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')
