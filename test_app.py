import unittest
from unittest.mock import patch
from app import app, get_actual_generations_per_unit, transform_data, production_average_per_hour, \
    production_sum_per_hour_of_day


class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_get_data_route(self):
        response = self.app.get('/data')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn('actual_generations_per_unit', data)

    @patch('app.requests.get')
    def test_get_actual_generations_per_unit(self, mock_get):
        mock_get.return_value.json.return_value = {'actual_generations_per_unit': [{'values': [
            {'start_date': '2022-12-01T00:00:00+02:00', 'end_date': '2022-12-01T01:00:00+02:00', 'value': 100}]}]}
        start_date = '2022-12-01T00:00:00+02:00'
        end_date = '2022-12-01T01:00:00+02:00'
        data = get_actual_generations_per_unit(start_date, end_date)
        self.assertIsInstance(data, dict)
        self.assertIn('actual_generations_per_unit', data)
        self.assertEqual(data['actual_generations_per_unit'][0]['values'][0]['value'], 100)

    def test_transform_data(self):
        data = {'actual_generations_per_unit': [
            {'start_date': '2022-12-01T00:00:00+02:00', 'end_date': '2022-12-01T01:00:00+02:00', 'values': [
                {'start_date': '2022-12-01T00:00:00+02:00', 'end_date': '2022-12-01T01:00:00+02:00', 'value': 100}]}]}
        df = transform_data(data)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 1)

    def test_production_average_per_hour(self):
        pass

    def test_production_sum_per_hour_of_day(self):
        pass


if __name__ == '__main__':
    unittest.main()
