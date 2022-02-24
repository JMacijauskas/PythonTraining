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

    def test_get_crypto_data_positive_path(self):
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

        # Testing if errors raised by parse_values function are also raised
        tracker.parse_values = MagicMock(side_effect=ValueError('False dictionary'))
        with self.assertRaises(ValueError) as err:
            tracker.get_crypto_data()
        self.assertEqual(str(err.exception), 'False dictionary')

    def test_get_crypto_data_error_path(self):
        """
        Testing if errors raised by requests.get function are handled
        class: CryptoTracker
        method: get_crypto_data
        """

        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)

        requests.get = MagicMock(side_effect=requests.exceptions.HTTPError())
        resp2 = tracker.get_crypto_data()
        self.assertEqual(resp2, {})

    def test_get_crypto_data_error_path2(self):
        """
        Testing if responses with error indication are handled
        class: CryptoTracker
        method: get_crypto_data
        """

        request_mock = {
            'Response': 'Error',
            'Message': 'fsyms is a required param.',
            'HasWarning': False,
            'Type': 2,
            'RateLimit': {},
            'Data': {},
            'ParamWithError': 'fsyms'}

        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        mock = MagicMock()
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

    def test_check_for_alarms_initial_run(self):
        """
        Test to see if first iteration of this function saves values as initial values
        class: CryptoTracker
        method: check_for_alarms
        """
        mock_dict = {
            'EUR': {'BTC': 34188.03419, 'ETH': 2381.51941, 'XRP': 0.64641},
            'USD': {'BTC': 38804.8118, 'ETH': 2702.7027, 'XRP': 0.73368}
        }

        mock_dict2 = {
            'EUR': {'BTTC': 3418.03419, 'ETTH': 238.51941, 'XRRP': 0.4641},
            'USD': {'BTTC': 3880.8118, 'ETTH': 270.7027, 'XRRP': 0.3368}
        }

        mock_dict3 = {
            'EUR': {'BTCC': 3188.03419, 'ETHH': 281.51941, 'XRPP': 0.6641},
            'USD': {'BTCC': 3804.8118, 'ETHH': 202.7027, 'XRPP': 0.78}
        }

        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        self.assertIsNone(tracker.init_data)

        tracker.compare = MagicMock(return_value=(True, 1.1, 1.1))

        # Testing case where input dict is empty
        alarms = tracker.check_for_alarms({})
        self.assertIsNone(tracker.init_data)
        self.assertEqual(alarms, [])
        self.assertFalse(alarms)

        alarms = tracker.check_for_alarms(mock_dict)
        self.assertDictEqual(tracker.init_data, mock_dict)
        self.assertEqual(alarms, [])
        self.assertFalse(alarms)

        # Testing if further runs do not change initial value
        for dic in (mock_dict2, mock_dict3):
            tracker.check_for_alarms(dic)
            self.assertIsNotNone(tracker.init_data)
            self.assertDictEqual(tracker.init_data, mock_dict)

    def test_check_for_alarms_negative(self):
        """
        Test to see if function return correct response with mocked function compare return None or False
        class: CryptoTracker
        method: check_for_alarms
        """

        mock_init_dict = {
            'EUR': {'BTC': 34188.03419, 'ETH': 2381.51941, 'XRP': 0.64641},
            'USD': {'BTC': 38804.8118, 'ETH': 2702.7027, 'XRP': 0.73368}
        }

        mock_dict = {
            'EUR': {'BTC': 1, 'ETH': 2, 'XRP': 3},
            'USD': {'BTC': 4, 'ETH': 5, 'XRP': 6}
        }

        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        tracker.init_data = mock_init_dict

        tracker.compare = MagicMock(return_value=(None, 1.1, 1.1))

        alarms = tracker.check_for_alarms(mock_dict)
        self.assertEqual(alarms, [])

        tracker.compare = MagicMock(return_value=(False, 1.2, 1.2))

        alarms = tracker.check_for_alarms(mock_dict)
        self.assertEqual(alarms, [])

    def test_check_for_alarms_positive(self):
        """
        Test to see if function return correct response with positive scenario, where alarms are raised
        class: CryptoTracker
        method: check_for_alarms
        """

        mock_init_dict = {
            'EUR': {'BTC': 34188.03419, 'ETH': 2381.51941, 'XRP': 0.64641},
            'USD': {'BTC': 38804.8118, 'ETH': 2702.7027, 'XRP': 0.73368}
        }

        mock_dict = {
            'EUR': {'BTC': 1.1, 'ETH': 2.1, 'XRP': 3.1},
            'USD': {'BTC': 4.1, 'ETH': 5.1, 'XRP': 6.1}
        }

        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        tracker.init_data = mock_init_dict

        tracker.compare = MagicMock(return_value=(True, 1.1, 1.1))
        alarms = tracker.check_for_alarms(mock_dict)
        self.assertEqual(len(alarms), 6)
        for alarm in alarms:
            self.assertIsInstance(alarm, Crypto_tracker.Alarm)
            self.assertIsInstance(alarm.crypto_name, str)
            self.assertIsInstance(alarm.currency, str)
            self.assertIsInstance(alarm.current_value, float)
            self.assertIsInstance(alarm.initial_value, float)
            self.assertIsInstance(alarm.deviation, float)

    def test_check_for_alarms_mixed(self):
        """
        Test to see if function return correct response with mixed (true, false, none) scenario, where alarms are raised
        class: CryptoTracker
        method: check_for_alarms
        """

        mock_init_dict = {
            'EUR': {'BTC': 34188.03419, 'ETH': 2381.51941, 'XRP': 0.64641},
            'USD': {'BTC': 38804.8118, 'ETH': 2702.7027, 'XRP': 0.73368}
        }

        mock_dict = {
            'EUR': {'BTC': 1.1, 'ETH': 2.1, 'XRP': 3.1},
            'USD': {'BTC': 4.1, 'ETH': 5.1, 'XRP': 6.1}
        }

        mock_compare_returns = (
            {'over_threshold': True, 'reference_value': 22, 'value_change': 12},
            {'over_threshold': False, 'reference_value': 1, 'value_change': 1},
            {'over_threshold': True, 'reference_value': 786.2, 'value_change': 13.88},
            {'over_threshold': False, 'reference_value': 1, 'value_change': 1},
            {'over_threshold': None, 'reference_value': 2, 'value_change': 2},
            {'over_threshold': True, 'reference_value': 1222, 'value_change': -19.99},
        )

        # tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        # tracker.init_data = mock_init_dict
        #
        # for compare_mock in mock_compare_returns:
        #     tracker.compare = MagicMock(
        #         return_value=(
        #             compare_mock['over_threshold'],
        #             compare_mock['reference_value'],
        #             compare_mock['value_change']
        #         )
        #     )
        #     alarms = tracker.check_for_alarms(mock_dict)
        #     self.assertEqual(len(alarms), 6)
        #     for alarm in alarms:
        #         self.assertIsInstance(alarm, Crypto_tracker.Alarm)
        #         self.assertIsInstance(alarm.crypto_name, str)
        #         self.assertIsInstance(alarm.currency, str)
        #         self.assertIsInstance(alarm.current_value, float)
        #         self.assertIsInstance(alarm.initial_value, float)
        #         self.assertIsInstance(alarm.deviation, float)


    def test_compare_initial(self):
        """
        Test to see if Alarms are correctly calculating change of each value with sample imput dict
        class: CryptoTracker
        method: compare
        """
        mock_init_data = {
            'EUR': {'BTC': 35000.035, 'ETH': 2000.5, 'XRP': 0.60001},
            'USD': {'BTC': 40000.90001, 'ETH': 2700, 'XRP': 0.75}
        }

        mock_input = {'num': 34188.03419, 'coin': 'BTC', 'curr': 'EUR'}

        tracker = Crypto_tracker.CryptoTracker([''], [''], 10)
        tracker.init_data = mock_init_data

        output_flag, ref_val, change = tracker.compare(mock_input['num'], mock_input['coin'], mock_input['curr'])
        self.assertFalse(output_flag)
        self.assertIsInstance(ref_val, float)
        self.assertEqual(ref_val, mock_init_data[mock_input['curr']][mock_input['coin']])
        self.assertIsInstance(change, float)
        self.assertEqual(change, -2.32)

    def test_compare_output1_and_output3_values(self):
        """
        Testing first (bool) and second (float) output evaluation correctness with one sample value in dict
        class: CryptoTracker
        method: compare
        """

        mock_init_data = {
            'EUR': {'BTC': 35000.035, 'ETH': 2000.5, 'XRP': 0.60001},
            'USD': {'BTC': 40000.90001, 'ETH': 2700, 'XRP': 0.75}
        }

        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        tracker.init_data = mock_init_data

        curr = 'EUR'
        coin = 'BTC'
        test_threshold = 15.2

        test_sample_ref = mock_init_data[curr][coin]
        tracker.threshold = test_threshold

        for thick in range(-200, 200, 4):  # 200 / 10 = 20% change
            change_perc = thick / 10
            test_sample = round(test_sample_ref * (1 + change_perc / 100), 5)
            output_flag, ref_val, change = tracker.compare(test_sample, coin, curr)
            self.assertEqual(change, change_perc)
            if abs(change_perc) >= test_threshold:
                self.assertTrue(output_flag)
            else:
                self.assertFalse(output_flag)

        # Same test with other sample value in dict
        curr = 'USD'
        coin = 'XRP'
        test_threshold = 12

        test_sample_ref = mock_init_data[curr][coin]
        tracker.threshold = test_threshold

        for thick in range(-200, 200, 2):   # 200 / 10 = 20% change
            change_perc = thick / 10
            test_sample = round(test_sample_ref * (1 + change_perc / 100), 5)
            output_flag, ref_val, change = tracker.compare(test_sample, coin, curr)
            self.assertEqual(change, change_perc)
            if abs(change_perc) >= test_threshold:
                self.assertTrue(output_flag)
            else:
                self.assertFalse(output_flag)

    def test_compare_init_data_access(self):
        """
        Testing first (bool) and second (float) output evaluation correctness with one sample value in dict
        class: CryptoTracker
        method: compare
        """

        mock_init_data = {
            'EUR': {'BTC': 0, 'ETH': 0, 'XRP': 0},
            'USD': {'lot': 0, 'eeth': 0, 'XeRP': 0},
            'RUP': {'all': 0, 'any': 0, 'XX': 0}
        }

        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)

        mock = MagicMock()
        mock_tier2 = MagicMock()
        mock_tier2.__getitem__.return_value = 777
        mock.__getitem__.return_value = mock_tier2

        tracker.init_data = mock

        for curr in mock_init_data:
            for coin in mock_init_data[curr]:
                c, ref, ch = tracker.compare(2, coin, curr)
                self.assertEqual(ref, 777)
        self.assertEqual(len(mock_tier2.mock_calls), 9)


if __name__ == '__main__':
    unittest.main()
