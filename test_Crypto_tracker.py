import unittest
from unittest.mock import MagicMock
import Crypto_tracker


# add coverage report
class TestCryptotracker(unittest.TestCase):
    def test_parse_values(self):
        sample_dict = {
            'A': {'A1': 100, 'A2': 0.1, 'A3': 1, 'A4': 99.999, 'A5': 0.0000001},
            'B': {'B1': 17.9, 'B2': 17.99, 'B3': 17.999, 'B4': 17.9999, 'B5': 17.99999, 'B6': 17.999999},
            'C': {'C1': 1, 'C2': 10, 'C3': 1000, 'C4': 10000, 'C5': 100000, 'C6': 1000000}
        }
        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        output = tracker.parse_values(sample_dict.copy())

        self.assertIsInstance(output, dict)
        self.assertEqual(len(output), len(sample_dict))
        self.assertEqual(output.keys(), sample_dict.keys())

        for val in sample_dict:
            for cases in sample_dict[val]:
                self.assertIsInstance(output[val][cases], float)

        tracker.coin_for_currency_to_coin_value = MagicMock(return_value=3.1)
        output = tracker.parse_values(sample_dict.copy())
        for val in sample_dict:
            for cases in sample_dict[val]:
                self.assertIsInstance(output[val][cases], float)

        tracker.coin_for_currency_to_coin_value = MagicMock(return_value=10)
        output = tracker.parse_values(sample_dict.copy())
        for val in sample_dict:
            for cases in sample_dict[val]:
                self.assertIsInstance(output[val][cases], int)

        tracker.coin_for_currency_to_coin_value = MagicMock(return_value='ADC')
        output = tracker.parse_values(sample_dict.copy())
        for val in sample_dict:
            for cases in sample_dict[val]:
                self.assertIsInstance(output[val][cases], str)

        tracker.coin_for_currency_to_coin_value = MagicMock(side_effect=ValueError('False Value'))
        with self.assertRaises(ValueError) as r:
            tracker.parse_values(sample_dict.copy())
        self.assertEqual(str(r.exception), 'False Value')

    def test_coin_for_currency_to_coin_value_positive(self):
        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        input_vals = (-1000000, -999999999, -99.99, -100, -10, -1, 1, 10, 100, 99.99, 999999999, 1000000)
        ref_output_vals = (0, 0, -0.01, -0.01, -0.1, -1, 1, 0.1, 0.01, 0.01, 0, 0)
        for i, inp in enumerate(input_vals):
            output_val = tracker.coin_for_currency_to_coin_value(inp)
            self.assertEqual(output_val, ref_output_vals[i])

    def test_coin_for_currency_to_coin_value_negative(self):
        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        with self.assertRaises(ZeroDivisionError):
            tracker.coin_for_currency_to_coin_value(0)

        with self.assertRaises(TypeError):
            tracker.coin_for_currency_to_coin_value('10')

    def test_get_crypto_data(self):
        c_coins = ['BTC', 'ETH', 'XRP']
        currencies = ['USD', 'EUR']
        tracker = Crypto_tracker.CryptoTracker(currencies, c_coins, 0)

        resp1 = tracker.get_crypto_data()

        self.assertIsInstance(resp1, dict)
        self.assertEqual(currencies, list(resp1.keys()))
        for currenc in resp1:
            self.assertEqual(c_coins, list(resp1[currenc].keys()))

        tracker.crypt_endpoint = 'https://min-api.cryptocompare.com/data/pricemulti'
        resp2 = tracker.get_crypto_data()

        self.assertEqual(resp2, {})


if __name__ == '__main__':
    unittest.main()
