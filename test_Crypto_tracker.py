import unittest
from unittest.mock import MagicMock
import requests
import Crypto_tracker


# add coverage report
class TestCryptotracker(unittest.TestCase):
    def test_parse_values(self):
        """
        Tests to see if function processes input dict correctly and how it handles errors
        class: CryptoTracker
        method: parse_values
        """
        sample_dict = {
            'A': {'A1': 100, 'A2': 0.1, 'A3': 1, 'A4': 99.999, 'A5': 0.0000001},
            'B': {'B1': 17.9, 'B2': 17.99, 'B3': 17.999, 'B4': 17.9999, 'B5': 17.99999, 'B6': 17.999999},
            'C': {'C1': 1, 'C2': 10, 'C3': 1000, 'C4': 10000, 'C5': 100000, 'C6': 1000000}
        }
        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        tracker.coin_for_currency_to_coin_value = MagicMock(return_value=1.1)
        output = tracker.parse_values(sample_dict.copy())

        # Testing if dictionary properties are the same after function call
        self.assertIsInstance(output, dict)
        self.assertEqual(len(output), len(sample_dict))
        self.assertEqual(output.keys(), sample_dict.keys())

        # Testing if mocked function 'coin_for_currency_to_coin_value' is called for every value of dictionaries
        mock = MagicMock(return_value=1)
        tracker.coin_for_currency_to_coin_value = mock
        tracker.parse_values(sample_dict.copy())
        self.assertEqual(mock.call_count, 17)

        # Testing if same exception is raised for function call, as for mocked function
        tracker.coin_for_currency_to_coin_value = MagicMock(side_effect=ValueError('False Value'))
        with self.assertRaises(ValueError) as r:
            tracker.parse_values(sample_dict.copy())
        self.assertEqual(str(r.exception), 'False Value')

    def test_coin_for_currency_to_coin_value_positive(self):
        """
        Test to see if calculations are executed as expected
        class: CryptoTracker
        method: coin_for_currency_to_coin_value
        """
        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        input_vals = (-1000000, -999999999, -99.99, -100, -10, -1, 1, 10, 100, 99.99, 999999999, 1000000)
        ref_output_vals = (0, 0, -0.01, -0.01, -0.1, -1, 1, 0.1, 0.01, 0.01, 0, 0)
        for i, inp in enumerate(input_vals):
            output_val = tracker.coin_for_currency_to_coin_value(inp)
            self.assertEqual(output_val, ref_output_vals[i])

    def test_coin_for_currency_to_coin_value_negative(self):
        """
        Test to see if calculations are executed as expected
        class: CryptoTracker
        method: coin_for_currency_to_coin_value
        """
        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        with self.assertRaises(ZeroDivisionError):
            tracker.coin_for_currency_to_coin_value(0)

        with self.assertRaises(TypeError):
            tracker.coin_for_currency_to_coin_value('10')

    def test_get_crypto_data(self):
        """
        Test to see if returned values are as expected
        class: CryptoTracker
        method: get_crypto_data
        """
        request_mock = {
            'EUR': {'BTC': 34188.03419, 'ETH': 2381.51941, 'XRP': 0.64641},
            'USD': {'BTC': 38804.8118, 'ETH': 2702.7027, 'XRP': 0.73368}
        }
        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        mock = MagicMock()
        mock().json.return_value = request_mock

        requests.get = mock
        tracker.parse_values = requests.get().json

        resp1 = tracker.get_crypto_data()

        # Testing if function output matches mocked requests.json response
        self.assertDictEqual(resp1, request_mock)

        # Testing if errors raised by get_crypto_data function are also raised
        tracker.parse_values = MagicMock(side_effect=ValueError('False dictionary'))
        with self.assertRaises(ValueError) as err:
            tracker.get_crypto_data()
        self.assertEqual(str(err.exception), 'False dictionary')

        # Testing if errors raised by requests.get function are handled
        requests.get = MagicMock(side_effect=requests.exceptions.HTTPError())
        resp2 = tracker.get_crypto_data()
        self.assertEqual(resp2, {})

        # Testing if responses with error indication are handled
        request_mock = {
            'Response': 'Error',
            'Message': 'fsyms is a required param.',
            'HasWarning': False,
            'Type': 2,
            'RateLimit': {},
            'Data': {},
            'ParamWithError': 'fsyms'}
        mock().json.return_value = request_mock
        requests.get = mock
        tracker.parse_values = requests.get().json

        tracker.crypt_endpoint = 'this_key_is_not_here'

        with self.assertRaises(ValueError) as errors:
            tracker.get_crypto_data()
        self.assertEqual(
            str(errors.exception),
            f"False URL or it's parameters: this_key_is_not_here"
        )

    def test_check_for_alarms(self):
        """
        Test to see if Alarms are captured as expected
        class: CryptoTracker
        method: check_for_alarms
        """
        request_mock = {
            'EUR': {'BTC': 34188.03419, 'ETH': 2381.51941, 'XRP': 0.64641},
            'USD': {'BTC': 38804.8118, 'ETH': 2702.7027, 'XRP': 0.73368}
        }

    def test_compare(self):
        """
        Test to see if Alarms are correctly calculating change of value
        class: CryptoTracker
        method: compare
        """
        mock_init_data = {
            'EUR': {'BTC': 35000.035, 'ETH': 2000.5, 'XRP': 0.60001},
            'USD': {'BTC': 40000.90001, 'ETH': 2700, 'XRP': 0.75}
        }
        # Testing regular output correctness with sample imput dict
        tracker = Crypto_tracker.CryptoTracker([''], [''], 10)
        tracker.init_data = mock_init_data
        mock_input = {'num': 34188.03419, 'coin': 'BTC', 'curr': 'EUR'}
        output_flag, ref_val, change = tracker.compare(mock_input['num'], mock_input['coin'], mock_input['curr'])
        self.assertFalse(output_flag)
        self.assertIsInstance(ref_val, float)
        self.assertEqual(ref_val, mock_init_data[mock_input['curr']][mock_input['coin']])
        self.assertIsInstance(change, float)
        self.assertEqual(change, -2.32)

        # Testing first (bool) and second (float) output evaluation correctness with one sample value in dict
        test_sample_ref = mock_init_data['EUR']['BTC']
        thick_change = 0.2
        init_change_perc = -20
        tracker.threshold = 15.2
        for thick in range(0, 200):
            change_perc = round(init_change_perc + thick_change * thick, 3)
            test_sample = round(test_sample_ref * (1 + change_perc / 100), 5)
            output_flag, ref_val, change = tracker.compare(test_sample, 'BTC', 'EUR')
            self.assertEqual(change, change_perc)
            if 29680.02968 >= test_sample or 40320.04032 <= test_sample:
                self.assertTrue(output_flag)
            else:
                self.assertFalse(output_flag)

        # Testing first (bool) and second (float) output evaluation correctness with other sample value in dict
        test_sample_ref = mock_init_data['USD']['XRP']
        thick_change = 0.4
        init_change_perc = -40
        tracker.threshold = 9.2
        for thick in range(0, 200):
            change_perc = round(init_change_perc + thick_change * thick, 3)
            test_sample = round(test_sample_ref * (1 + change_perc / 100), 5)
            output_flag, ref_val, change = tracker.compare(test_sample, 'XRP', 'USD')
            self.assertEqual(change, change_perc)
            if 0.681 >= test_sample or 0.819 <= test_sample:
                self.assertTrue(output_flag)
            else:
                self.assertFalse(output_flag)

        mock = MagicMock()
        mock.get.return_value = 1
        tracker.init_data = mock
        for curr in mock_init_data:
            for coin in curr:
                tracker.compare(2, 'ETH', 'USD')
        self.assertEqual(mock.call_count, 7)


if __name__ == '__main__':
    unittest.main()
