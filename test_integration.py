import unittest
from unittest.mock import patch
from main import fetch_and_notify
from weather_api import get_weather


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.valid_data = {"city": "Moscow", "temperature": 15.0, "description": "ясно"}

    @patch("main.get_weather")
    @patch("main.send_notification")
    def test_successful_integration(self, mock_notify, mock_get_weather):
        mock_get_weather.return_value = self.valid_data
        mock_notify.return_value = True

        result = fetch_and_notify("Moscow", "fake_api_key")
        self.assertTrue(result)
        mock_notify.assert_called_once_with(self.valid_data)

    @patch("main.get_weather", return_value=None)
    def test_weather_data_none(self, mock_get_weather):
        result = fetch_and_notify("Moscow", "fake_api_key")
        self.assertFalse(result)




    @patch("main.get_weather", side_effect=ValueError("API error"))
    def test_get_weather_exception(self, mock_get_weather):
        result = fetch_and_notify("Moscow", "fake_api_key")
        self.assertFalse(result)
