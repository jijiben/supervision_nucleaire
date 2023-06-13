import json
import unittest
from unittest import mock
from unittest.mock import patch
from app import app, get_actual_generations_per_unit, transform_data, production_average_per_hour, \
    production_sum_per_hour_of_day, request_new_access_token, get_access_token


class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        self.cache = mock.MagicMock()
        app.config.from_pyfile('config.py')

        with open('test.json') as f:
            self.actual_generations_per_unit = json.load(f)
            self.data = self.actual_generations_per_unit.get('actual_generations_per_unit', [])

    def test_get_access_token_from_cache(self):
        """Test for related function :get_access_token"""
        # Mock the cache to return a specific access token
        self.cache.get.return_value = 'your_access_token'

        # Patch the cache object in app.py with the mock cache
        with mock.patch('app.cache', self.cache):
            access_token = get_access_token()

        # Assert that the access token returned is the expected one
        self.assertEqual(access_token, 'your_access_token')

        # Assert that the cache.get method was called with the correct argument
        self.cache.get.assert_called_once_with('access_token')

    def test_get_access_token_request_new_token(self):
        """Test for related function :get_access_token"""
        # Mock the cache to return None for the access token
        self.cache.get.return_value = None
        self.cache.set.return_value = None

        # Patch the cache object and request_new_access_token function in app.py with the mock objects
        with mock.patch('app.cache', self.cache), \
                mock.patch('app.request_new_access_token') as mock_request_token:
            # Mock the request_new_access_token function to return a new access token
            mock_request_token.return_value = ('new_access_token', 3600)

            # Call the get_access_token function
            access_token = get_access_token()

        # Assert that the access token returned is the new access token
        self.assertEqual(access_token, 'new_access_token')

        # Assert that the cache.get method and cache.set method were called with the correct arguments
        self.cache.get.assert_called_once_with('access_token')
        self.cache.set.assert_called_once_with('access_token', 'new_access_token', timeout=3600)

        # Assert that the request_new_access_token function was called
        mock_request_token.assert_called_once()

    def test_request_new_access_token(self):
        """Test for related function :request_new_access_token"""
        expected_token = 'new_access_token'
        expected_expiration = 3600

        # Create a mock response with the expected access token and expiration
        expected_response = {
            'access_token': expected_token,
            'expires_in': expected_expiration,
            "token_type": "Bearer",
        }
        mock_response = mock.MagicMock()
        mock_response.json.return_value = expected_response

        # Patch the requests.post function to return the mock response
        with mock.patch('app.request_new_access_token') as mock_request_token, \
                mock.patch('app.requests.post') as mock_post:
            mock_post.return_value = mock_response

            # Mock the request_new_access_token function to return the expected token and expiration
            mock_request_token.return_value = expected_token, expected_expiration

            # Call the request_new_access_token function
            token, expiration = request_new_access_token()

        # Assert that the token and expiration returned are the expected ones
        self.assertEqual(token, expected_token)
        self.assertEqual(expiration, expected_expiration)

    def test_get_data_route(self):
        """Test for related function :get_data_route"""
        # Send a GET request to the '/data' route
        response = self.app.get('/data')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Get the JSON data from the response
        data = response.get_json()

        # Assert that the data is an instance of dict
        self.assertIsInstance(data, dict)

        # Assert that the 'actual_generations_per_unit' key is present in the data
        self.assertIn('actual_generations_per_unit', data)

    @patch('app.requests.get')
    def test_get_actual_generations_per_unit(self, mock_get):
        """Test for related function :get_actual_generations_per_unit"""
        # Mock the response of the requests.get function to return a specific JSON data
        mock_get.return_value.json.return_value = {'actual_generations_per_unit': [{'values': [
            {'start_date': '2022-12-01T00:00:00+02:00', 'end_date': '2022-12-01T01:00:00+02:00', 'value': 100}]}]}

        start_date = '2022-12-01T00:00:00+02:00'
        end_date = '2022-12-01T01:00:00+02:00'

        # Call the get_actual_generations_per_unit function
        data = get_actual_generations_per_unit(start_date, end_date)

        # Assert that the data returned is an instance of dict
        self.assertIsInstance(data, dict)

        # Assert that the 'actual_generations_per_unit' key is present in the data
        self.assertIn('actual_generations_per_unit', data)

        # Assert that the value in the data matches the expected value
        self.assertEqual(data['actual_generations_per_unit'][0]['values'][0]['value'], 100)

    def test_production_sum_per_hour_of_day(self):
        """Test for related function :production_sum_per_hour_of_day"""
        expected_result = {'2022-12-01': {'Hour 00': 1287.5, 'Hour 01': 1288.5, 'Hour 02': 1289.5,
                                          'Hour 03': 1289.5, 'Hour 04': 1289.5, 'Hour 05': 1290.0,
                                          'Hour 06': 1290.0, 'Hour 07': 1290.0, 'Hour 08': 1289.5,
                                          'Hour 09': 1289.5, 'Hour 10': 1289.5, 'Hour 11': 1289.0,
                                          'Hour 12': 1288.0, 'Hour 13': 1288.0, 'Hour 14': 1287.0,
                                          'Hour 15': 1287.0, 'Hour 16': 1287.0, 'Hour 17': 1288.0,
                                          'Hour 18': 1287.0, 'Hour 19': 1287.0, 'Hour 20': 1287.0,
                                          'Hour 21': 1287.0, 'Hour 22': 1288.0, 'Hour 23': 1289.0}}

        # Call the production_sum_per_hour_of_day function with the test data
        result = production_sum_per_hour_of_day(self.data)

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_production_average_per_hour(self):
        """Test for related function :production_average_per_hour"""
        pass

    def test_transform_data(self):
        """Test for related function :transform_data"""

        pass
