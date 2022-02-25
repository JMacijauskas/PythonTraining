import typing
import unittest
from unittest.mock import MagicMock
import requests
import Crypto_tracker


# add coverage report
class TestCryptotracker(unittest.TestCase):
    def test_parse_values(self):
        """
        Testing if dictionary properties are the same after function call
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

        self.assertIsInstance(output, dict)
        self.assertEqual(len(output), len(sample_dict))
        self.assertEqual(output.keys(), sample_dict.keys())

    def test_parse_values_sub_functin_call(self):
        """
        Testing if mocked function 'coin_for_currency_to_coin_value' is called for every value of dictionaries
        class: CryptoTracker
        method: parse_values
        """

        sample_dict = {
            'A': {'A1': 100, 'A2': 0.1, 'A3': 1, 'A4': 99.999, 'A5': 0.0000001},
            'B': {'B1': 17.9, 'B2': 17.99, 'B3': 17.999, 'B4': 17.9999, 'B5': 17.99999, 'B6': 17.999999},
            'C': {'C1': 1, 'C2': 10, 'C3': 1000, 'C4': 10000, 'C5': 100000, 'C6': 1000000}
        }
        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)

        mock = MagicMock(return_value=1)
        tracker.coin_for_currency_to_coin_value = mock

        tracker.parse_values(sample_dict.copy())
        self.assertEqual(mock.call_count, 17)

    def test_parse_values_exceptions(self):
        """
        Testing if same exception is raised for function call, as for mocked function
        class: CryptoTracker
        method: parse_values
        """

        sample_dict = {
            'A': {'A1': 100, 'A2': 0.1, 'A3': 1, 'A4': 99.999, 'A5': 0.0000001},
            'B': {'B1': 17.9, 'B2': 17.99, 'B3': 17.999, 'B4': 17.9999, 'B5': 17.99999, 'B6': 17.999999},
            'C': {'C1': 1, 'C2': 10, 'C3': 1000, 'C4': 10000, 'C5': 100000, 'C6': 1000000}
        }
        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)

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
        Testing if function output matches mocked requests.json response
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
        self.assertDictEqual(resp1, request_mock)

    def test_get_crypto_data_exception_path(self):
        """
        Testing if errors raised by parse_values function are also raised
        class: CryptoTracker
        method: get_crypto_data
        """

        requests.get = MagicMock()
        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)

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
        self.assertDictEqual(resp2, {})

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

        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        self.assertIsNone(tracker.init_data)

        tracker.compare = MagicMock(return_value=(True, 1.1, 1.1))

        alarms = tracker.check_for_alarms(mock_dict)
        self.assertDictEqual(tracker.init_data, mock_dict)
        self.assertListEqual(alarms, [])
        self.assertFalse(alarms)

    def test_check_for_alarms_failed_init(self):
        """
        Testing case where input dict is empty
        class: CryptoTracker
        method: check_for_alarms
        """

        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)

        alarms = tracker.check_for_alarms({})
        self.assertIsNone(tracker.init_data)
        self.assertEqual(alarms, [])
        self.assertFalse(alarms)

    def test_check_for_alarms_initial_value_persist(self):
        """
        Testing if further runs do not change initial value
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
        tracker.init_data = mock_dict

        tracker.compare = MagicMock(return_value=(False, 1.1, 1.1))

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
        self.assertListEqual(alarms, [])

        tracker.compare = MagicMock(return_value=(False, 1.2, 1.2))

        alarms = tracker.check_for_alarms(mock_dict)
        self.assertListEqual(alarms, [])

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

        dict_keys = []
        for curr in mock_init_dict:
            for coin in mock_init_dict[curr]:
                dict_keys.append((curr, coin))

        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        tracker.init_data = mock_init_dict

        tracker.compare = MagicMock(return_value=(True, 1.1, 1.2))
        alarms = tracker.check_for_alarms(mock_dict)
        self.assertEqual(len(alarms), 6)
        for i, (curr, coin) in enumerate(dict_keys):
            self.assertIsInstance(alarms[i], Crypto_tracker.Alarm)
            self.assertEqual(alarms[i].crypto_name, coin)
            self.assertEqual(alarms[i].currency, curr)
            self.assertEqual(alarms[i].current_value, mock_dict[curr][coin])
            self.assertEqual(alarms[i].initial_value, 1.1)
            self.assertEqual(alarms[i].deviation, 1.2)

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
            'EUR': {'BTC': 888.8, 'ETH': 333, 'XRP': 33.3},
            'USD': {'BTC': 411.11, 'ETH': 5.1, 'XRP': 22.1}
        }

        expected_return = [
            Crypto_tracker.Alarm('BTC', 'EUR', 888.8, 22, 12),
            Crypto_tracker.Alarm('XRP', 'EUR', 33.3, 786.2, 13.88),
            Crypto_tracker.Alarm('XRP', 'USD', 22.1, 1222, -19.99)
        ]

        dict_keys = []
        for curr in mock_init_dict:
            for coin in mock_init_dict[curr]:
                dict_keys.append((curr, coin))

        mock_compare_returns = (
            (True, 22, 12),
            (False, 1, 1),
            (True, 786.2, 13.88),
            (False, 1, 1),
            (None, 2, 2),
            (True, 1222, -19.99),
        )

        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        tracker.init_data = mock_init_dict

        mock = MagicMock(side_effect=mock_compare_returns)
        tracker.compare = mock

        alarms = tracker.check_for_alarms(mock_dict)
        self.assertEqual(len(alarms), 3)
        self.assertListEqual(alarms, expected_return)

        for i, expected_return_val in enumerate(expected_return):
            self.assertIsInstance(alarms[i], Crypto_tracker.Alarm)
            self.assertEqual(alarms[i].crypto_name, expected_return_val.crypto_name)
            self.assertEqual(alarms[i].currency, expected_return_val.currency)
            self.assertEqual(alarms[i].current_value, expected_return_val.current_value)
            self.assertEqual(alarms[i].initial_value, expected_return_val.initial_value)
            self.assertEqual(alarms[i].deviation, expected_return_val.deviation)

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

        curr = 'EUR'
        coin = 'BTC'
        test_threshold = 15.2

        self.compare_output_helper(curr, coin, test_threshold)

        # Same test with other sample value in dict
        curr = 'USD'
        coin = 'XRP'
        test_threshold = 12

        self.compare_output_helper(curr, coin, test_threshold)

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
                output_flag, ref_val, change = tracker.compare(2, coin, curr)
                self.assertEqual(ref_val, 777)
        self.assertEqual(len(mock_tier2.mock_calls), 9)

    def test_Alarm_str_change_indication(self):
        """
        Test to see if Alarms are correctly calculating change of each value with sample imput dict
        class: Alarm
        method: __repr__
        """

        sample_inp = [
            Crypto_tracker.Alarm('BTC', 'EUR', 888.8, 22, 12),
            Crypto_tracker.Alarm('XRP', 'EUR', 33.3, 786.2, 13.88),
            Crypto_tracker.Alarm('XRP', 'USD', 22.1, 1222, -19.99),
            Crypto_tracker.Alarm('BTC', 'EUR', 99.8, 99, 99),
            Crypto_tracker.Alarm('XRP', 'EUR', 99.3, 786.2, 13.88),
            Crypto_tracker.Alarm('XRP', 'USD', 99.1, 1222, -20)
        ]

        str_sample_inp = [str(x) for x in sample_inp]

        string_format_drop = '{} value dropped by {}%, from {} {} to {} {}'

        for i, strings in enumerate(str_sample_inp):
            string_alarm = string_format_drop.format(sample_inp[i].crypto_name,
                                                     sample_inp[i].deviation,
                                                     sample_inp[i].initial_value,
                                                     sample_inp[i].currency,
                                                     sample_inp[i].current_value,
                                                     sample_inp[i].currency)
            if sample_inp[i].deviation < 0:
                self.assertEqual(strings, string_alarm)
            else:
                self.assertEqual(strings, string_alarm.replace('dropped', 'raised'))

    def test_quantify_below_limit(self):
        """
        Test to if function correctly returns string with length lower than limit
        class: Sender
        method: quantify
        """

        str_inp = ('Some text expression', 'some symols !@#$,..)', '\nsome\nlines\nto\nsee', '123987')
        str_inp_generator = (x for x in str_inp)

        str_out = '\n' + '\n'.join(str_inp)

        sender = Crypto_tracker.Sender(False)

        new_generator = sender.quantify(str_inp_generator)
        self.assertIsInstance(new_generator, typing.Generator)
        self.assertEqual(new_generator.__next__(), str_out)
        self.assertRaises(StopIteration, new_generator.__next__)

    def test_quantify_below_at_limit(self):
        """
        Test to if function correctly returns string with length equal to limit
        class: Sender
        method: quantify
        """

        str_inp = ('Some text expression', 'some symols !@#$,..)', '\nsome\nlines\nto\nsee', '123987')
        str_inp_generator = (x for x in str_inp)

        str_out = '\n' + '\n'.join(str_inp)
        limit = len(str_out)

        sender = Crypto_tracker.Sender(False)
        sender.message_lim = limit

        new_generator = sender.quantify(str_inp_generator)
        self.assertIsInstance(new_generator, typing.Generator)
        self.assertEqual(new_generator.__next__(), str_out)
        self.assertRaises(StopIteration, new_generator.__next__)

    def test_quantify_below_over_limit(self):
        """
        Test to if function correctly returns string with length equal to limit
        class: Sender
        method: quantify
        """

        str_inp = ('Some text expression', 'some', 'symols', '!@#$', '..,)', '\nsome\nlines\nto\nsee', '123987')
        str_inp_generator = (x for x in str_inp)

        str_out = '\n' + '\n'.join(str_inp)

        expected_output_parts = (
            '',
            '\nSome text expression',
            '\nsome\nsymols\n!@#$',
            '\n..,)',
            '\n\nsome\nlines\nto\nsee',
            '\n123987'
        )

        limit = 20

        sender = Crypto_tracker.Sender(False)
        sender.message_lim = limit

        new_generator = sender.quantify(str_inp_generator)
        self.assertIsInstance(new_generator, typing.Generator)
        for output in expected_output_parts:
            message_iter = new_generator.__next__()
            self.assertEqual(message_iter, output)
        self.assertRaises(StopIteration, new_generator.__next__)

    def compare_output_helper(self, currenc, coin_name, threshold):
        mock_init_data = {
            'EUR': {'BTC': 35000.035, 'ETH': 2000.5, 'XRP': 0.60001},
            'USD': {'BTC': 40000.90001, 'ETH': 2700, 'XRP': 0.75}
        }

        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        tracker.init_data = mock_init_data

        test_sample_ref = mock_init_data[currenc][coin_name]
        tracker.threshold = threshold

        for thick in range(-200, 200, 4):  # 200 / 10 = 20% change
            change_perc = thick / 10
            test_sample = round(test_sample_ref * (1 + change_perc / 100), 5)
            output_flag, ref_val, change = tracker.compare(test_sample, coin_name, currenc)
            self.assertEqual(change, change_perc)
            if abs(change_perc) >= threshold:
                self.assertTrue(output_flag)
            else:
                self.assertFalse(output_flag)


if __name__ == '__main__':
    unittest.main()
