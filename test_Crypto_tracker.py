import unittest
import Crypto_tracker


class TestCryptotracker(unittest.TestCase):
    def test_parse_values_positive(self):
        sample_dict = {
            'A': {'A1': 100, 'A2': 0.1, 'A3': 1, 'A4': 99.999, 'A5': 0.0000001},
            'B': {'B1': 17.9, 'B2': 17.99, 'B3': 17.999, 'B4': 17.9999, 'B5': 17.99999, 'B6': 17.999999},
            'C': {'C1': 1, 'C2': 10, 'C3': 1000, 'C4': 10000, 'C5': 100000, 'C6': 1000000}
        }
        tracker = Crypto_tracker.CryptoTracker([''], [''], 0)
        output = tracker.parse_values(sample_dict)

        self.assertIsInstance(output, dict)
        self.assertEqual(len(output), len(sample_dict))
        # self.assertEqual(output.keys(), sample_dict.keys())
        for val in sample_dict:
            for case in sample_dict[val]:
                expect_val = round(1 / sample_dict[val][case], 5)
                print(f'{output[val]} -- {sample_dict[val]}')
                print(f'{output[val][case]} -- {expect_val}')
                self.assertEqual(output[val][case], expect_val)


if __name__ == '__main__':
    unittest.main()
