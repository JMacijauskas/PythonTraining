import time
from typing import NamedTuple, Iterable, Generator
import requests
import os
import twilio.rest
from twilio.rest import Client
from dotenv import load_dotenv
import argparse
import logging


load_dotenv()  # Load .env stored environment variables in root add to main

"""
1. send request
2. process response json
3. evaluate state
4. send warnings if needed

Nice to add:
command line commands ( currency/coin_list/decimal_point)
ranges
higher limits
background functionality
server
"""


# Named tuple class for data of alarms
class Alarm(NamedTuple):
    crypto_name: str
    currency: str
    current_value: float
    initial_value: float
    deviation: float

    def __repr__(self):
        if self.deviation < 0:
            direction = 'dropped'
        else:
            direction = 'raised'
        return (
            f'{self.crypto_name} value {direction} by {self.deviation}%,'
            f' from {self.initial_value} {self.currency} to {self.current_value} {self.currency}'
        )


class HelpInfo(NamedTuple):
    period: str
    crypto: str
    currency: str
    threshold: str
    sms: str


def parse_cmd_args() -> argparse.Namespace:
    help_info = HelpInfo(
        'Time how often requests will be issued, in seconds. (default: %(default)s)',
        'List of crypto currency short names, that will be tracked. (default: %(default)s)',
        'List of currency short names, that will be used for evaluation. (default: %(default)s)',
        'Percentage value of threshold for tracking signals. (default: %(default)s)',
        'Whether or not sms notification should be sent. (default: %(default)s)'
    )
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--period', help=help_info.period, default=60, type=int)
    parser.add_argument('-c', '--crypto', help=help_info.crypto, default=('BTC', 'ETH', 'XRP'), nargs='*')
    parser.add_argument('-cr', '--currency', help=help_info.currency, default=('USD', 'EUR'), nargs='*')
    parser.add_argument('-t', '--threshold', help=help_info.threshold, default=10, type=float)
    parser.add_argument('-s', '--sms', help=help_info.sms, action='store_false')
    args = parser.parse_args()
    logging.info(f'Starting with arguments {args}')
    return args


class CryptoTracker:
    """
    API to track crypto can be accessed:
    https://www.cryptocompare.com/cryptopian/api-keys
    """
    def __init__(self, currency_iter: Iterable[str], crypto_coins: Iterable[str], limit: int):
        self.crypto_api_key = os.getenv('CRYPTO_API_KEY')
        self.currencies = currency_iter
        self.crypto_names = crypto_coins
        self.crypt_endpoint = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms={}&api_key={}'.format(
            ','.join(self.currencies),
            ','.join(self.crypto_names),
            self.crypto_api_key
        )
        self.init_data = None
        self.threshold = limit

    def get_crypto_data(self) -> dict:
        try:
            response = requests.get(self.crypt_endpoint)
        except requests.exceptions.HTTPError:
            logging.warning('Connection issue has occurred, check connection and try again.')
            return {}
        if response.json().get('Response') == "Error":
            raise ValueError(f"False URL or it's parameters: {self.crypt_endpoint}")
        else:
            changed_resp = self.parse_values(response.json())
            logging.info('Crypto coin data was received.')
            logging.debug(changed_resp)
            return changed_resp

    @staticmethod
    def coin_for_currency_to_coin_value(coins_per_currency: float) -> float:
        return round(1 / coins_per_currency, 5)

    def parse_values(self, json_data: dict) -> dict:
        for currency in json_data:
            for coin in json_data[currency]:
                json_data[currency][coin] = self.coin_for_currency_to_coin_value(json_data[currency][coin])
        return json_data

    def check_for_alarms(self, json_dict: dict) -> list[Alarm]:
        alarm_list = []
        if self.init_data is None:
            self.init_data = json_dict
        else:
            for currency in json_dict:
                for coins in json_dict[currency]:
                    value = json_dict[currency][coins]
                    over_threshold, reference_value, value_change = self.compare(value, coins, currency)
                    if over_threshold is not None:
                        alarm_list.append(Alarm(coins, currency, value, reference_value, value_change))
        logging.debug(f'Detected alarms: {alarm_list}')
        return alarm_list

    def compare(self, num: float, coin: str, curr: str) -> tuple[bool, float, float]:
        ref_val = self.init_data[curr][coin]
        change = round((num - ref_val) / ref_val * 100, 3)
        return abs(change) >= self.threshold, ref_val, change


class Sender:
    """
    Twillio API used to send sms can be accessed:
    https://www.twilio.com/console/projects/summary
    """
    def __init__(self, should_send):
        self.account_sid_twill = os.getenv('TWILIO_ACCOUNT_SID')
        self.secret_key_twill = os.getenv('TWILIO_AUTH_TOKEN')
        self.num_twill = os.getenv('TWILIO_NUMBER')
        self.user_number = os.getenv('USER_NUMBER')
        self.message_lim = 1600
        self.template_sms = ''
        self.sms_send = should_send

    def sending(self, data: list[Alarm]) -> None:
        alarm_str_generator = (str(alarm) for alarm in data)  # generator
        quants = self.quantify(alarm_str_generator)
        client = Client(self.account_sid_twill, self.secret_key_twill)
        for message in quants:
            logging.info(f'Message ready: {message}')
            if not self.sms_send:
                continue
            try:
                message_sent = client.messages.create(
                    body=f'{message}',
                    from_=f'{self.num_twill}',
                    to=f'{self.user_number}'
                )
            except twilio.rest.TwilioException as tw_err:
                logging.error(tw_err)
                logging.warning('SMS sending was initiated, but failed.')
            else:
                logging.info(f'SMS was sent with identification code: {message_sent.sid}')

    def quantify(self, alarms: Generator[str, None, None]) -> Generator[str, None, None]:
        full_message = ''
        for alarm in alarms:
            if len(alarm) + len(full_message) < self.message_lim:
                full_message += '\n' + alarm
            else:
                yield full_message
                full_message = '\n' + alarm
        yield full_message


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    arguments = parse_cmd_args()
    period = arguments.period

    new_track = CryptoTracker(arguments.currency, arguments.crypto, arguments.threshold)
    sendin = Sender(arguments.sms)
    while True:
        new_vals = new_track.get_crypto_data()
        alarms_in_list = new_track.check_for_alarms(new_vals)
        if alarms_in_list:
            sendin.sending(alarms_in_list)
        logging.info(f'wait {period}s')
        time.sleep(period)

