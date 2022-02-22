import time
import typing
import requests
import os

import twilio.rest
from twilio.rest import Client
from dotenv import load_dotenv
import argparse
import logging


load_dotenv()  # Load .env stored environment variables in root

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
# TODO: add error handling


# Named tuple class for data of alarms
class Alarm(typing.NamedTuple):
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


def parse_cmd_args() -> argparse.Namespace:
    args_dict = {
        'period': {
            'name1': '-p',
            'name2': '--period',
            'help': 'Time how often requests will be issued, in seconds. (default: %(default)s)',
            'default': 60,
            'type': int
        },
        'crypto': {
            'name1': '-c',
            'name2': '--crypto',
            'help': 'List of crypto currency short names, that will be tracked. (default: %(default)s)',
            'default': ('BTC', 'ETH', 'XRP'),
            'type': str,
            'nargs': '*'
        },
        'currencies': {
            'name1': '-cr',
            'name2': '--currencies',
            'help': 'List of currency short names, that will be used for evaluation. (default: %(default)s)',
            'default': ('USD', 'EUR'),
            'type': str,
            'nargs': '*'
        },
        'threshold': {
            'name1': '-t',
            'name2': '--threshold',
            'help': 'Percentage value of threshold for tracking signals. (default: %(default)s)',
            'default': 10,
            'type': float
        },
        'sms': {
            'name1': '-s',
            'name2': '--sms',
            'help': 'Whether or not sms notification should be sent. (default: %(default)s)',
            'default': 0,
            'type': int
        }
    }
    parser = argparse.ArgumentParser()
    for arg in args_dict:
        if 'nargs' in args_dict[arg].keys():
            parser.add_argument(
                args_dict[arg]['name1'],
                args_dict[arg]['name2'],
                help=args_dict[arg]['help'],
                default=args_dict[arg]['default'],
                type=args_dict[arg]['type'],
                nargs=args_dict[arg]['nargs']
            )
        else:
            parser.add_argument(
                args_dict[arg]['name1'],
                args_dict[arg]['name2'],
                help=args_dict[arg]['help'],
                default=args_dict[arg]['default'],
                type=args_dict[arg]['type']
            )
    args = parser.parse_args()
    logging.info(f'Starting with arguments {args}')
    return args


class CryptoTracker:
    """
    API to track crypto can be accessed:
    https://www.cryptocompare.com/cryptopian/api-keys
    """
    def __init__(self, currency_iter: typing.Iterable[str], crypto_coins: typing.Iterable[str], limit: int):
        try:
            self.crypto_api_key = os.environ['CRYPTO_API_KEY']
        except KeyError as k_err:
            logging.error(k_err)
            logging.warning('Missing required environment variable, check environment variables.')

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
            changed_resp = self.parse_values(response.json())
            logging.info('Crypto coin data was received.')
            logging.debug(changed_resp)
            return changed_resp
        except requests.exceptions.HTTPError as http_err:
            logging.error(http_err)
            logging.warning('Connection issue has occurred, check connection and try again.')

    @staticmethod
    def parse_values(json_data: dict) -> dict:
        for currency in json_data:
            for coin in json_data[currency]:
                json_data[currency][coin] = round(1 / json_data[currency][coin], 5)
        return json_data

    def check_for_alarms(self, json_dict: dict) -> list[Alarm]:
        alarm_list = []
        if self.init_data is None:
            self.init_data = json_dict
        else:
            for currency in json_dict:
                for coins in json_dict[currency]:
                    value = json_dict[currency][coins]
                    evaluation = self.compare(value, coins, currency)
                    if evaluation is not None:
                        alarm_list.append(Alarm(coins, currency, value, evaluation[0], evaluation[1]))
        logging.debug(f'Detected alarms: {alarm_list}')
        return alarm_list

    def compare(self, num: float, coin: str, curr: str) -> tuple[float, float]:
        ref_val = self.init_data[curr][coin]
        change = round((num - ref_val) / ref_val * 100, 3)
        if abs(change) >= self.threshold:
            return ref_val, change


class Sender:
    """
    Twillio API used to send sms can be accessed:
    https://www.twilio.com/console/projects/summary
    """
    def __init__(self, bool_send):
        try:
            self.account_sid_twill = os.environ['TWILIO_ACCOUNT_SID']
            self.secret_key_twill = os.environ['TWILIO_AUTH_TOKEN']
            self.num_twill = os.environ['TWILIO_NUMBER']
            self.user_number = os.environ['USER_NUMBER']
        except KeyError as k_err:
            logging.error(k_err)
            logging.warning('Missing required environment variable, check environment variables.')

        self.message_lim = 1600
        self.template_sms = ''
        self.sms_send = bool_send

    def sending(self, data: list[Alarm]) -> None:
        alarm_str_generator = (str(alarm) for alarm in data)  # generator
        quants = self.quantify(alarm_str_generator)
        client = Client(self.account_sid_twill, self.secret_key_twill)
        for message in quants:
            logging.info(f'Message ready: {message}')
            if self.sms_send:
                try:
                    message_sent = client.messages.create(
                        body=f'{message}',
                        from_=f'{self.num_twill}',
                        to=f'{self.user_number}'
                    )
                    logging.info(f'SMS was sent with identification code: {message_sent.sid}')
                except twilio.rest.TwilioException as tw_err:
                    logging.error(tw_err)
                    logging.warning('SMS sending was initiated, but failed.')

    def quantify(self, alarms: typing.Generator[str, None, None]) -> typing.Generator[str, None, None]:
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

    new_track = CryptoTracker(arguments.currencies, arguments.crypto, arguments.threshold)
    sendin = Sender(arguments.sms)
    while True:
        new_vals = new_track.get_crypto_data()
        alarms_in_list = new_track.check_for_alarms(new_vals)
        if alarms_in_list:
            sendin.sending(alarms_in_list)
        logging.info(f'wait {period}s')
        time.sleep(period)

