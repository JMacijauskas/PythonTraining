import time
import typing
import requests
import os
from twilio.rest import Client
from dotenv import load_dotenv
import sys


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


class SysArgs:
    def __init__(self, passed_args):
        self.args = passed_args
        self.args_dict = {
            'period': '-p',
            'crypto_list': '-c',
            'currencies': '-cr',
            'threshold': '-t'
        }

    def set_period(self):
        for possible_arg in self.args:
            for arg in self.args_dict:
                if arg == possible_arg:
                    pass


class CryptoTracker:
    """
    API to track crypto can be accessed:
    https://www.cryptocompare.com/cryptopian/api-keys
    """
    def __init__(self):
        self.crypto_api_key = os.getenv('CRYPTO_API_KEY')
        self.currencies = ('USD', 'EUR')
        self.crypto_names = ('BTC', 'ETH', 'XRP')
        self.crypt_endpoint = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms={}&api_key={}'.format(
            ','.join(self.currencies),
            ','.join(self.crypto_names),
            self.crypto_api_key
        )
        self.init_data = None
        # self.period = 60
        self.threshold = 0.001

    def get_crypto_data(self) -> dict:
        response = requests.get(self.crypt_endpoint)
        changed_resp = self.parse_values(response.json())
        print(changed_resp)
        return changed_resp

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
    def __init__(self):
        self.account_sid_twill = os.getenv('TWILIO_ACCOUNT_SID')
        self.secret_key_twill = os.getenv('TWILIO_AUTH_TOKEN')
        self.num_twill = os.getenv('TWILIO_NUMBER')
        self.user_number = os.getenv('USER_NUMBER')
        self.message_lim = 1600
        self.template_sms = ''

    def sending(self, data):
        data_text = self.process_alarm_data(data)
        quants = self.quantify(data_text)
        client = Client(self.account_sid_twill, self.secret_key_twill)
        for message in quants:
            print(message)
            # message_sent = client.messages.create(
            #     body=f'{message}',
            #     from_=f'{self.num_twill}',
            #     to=f'{self.user_number}'
            # )
            # print(message_sent.sid)

    @staticmethod
    def process_alarm_data(alarms: list[Alarm]) -> list:
        # takes list of data with alarm class for each coin:
        # crypto name, currency, current value, initial value, change %
        text_alarms = []
        for alarm in alarms:
            alarm_str = f'{alarm}'
            text_alarms.append(alarm_str)
            return text_alarms

    def quantify(self, alarms: list):
        full_message = ''
        for alarm in alarms:
            if len(alarm) + len(full_message) < self.message_lim:
                full_message += '\n' + alarm
            else:
                yield full_message
                full_message = '\n' + alarm
        yield full_message


if __name__ == '__main__':
    period = 60
    print(sys.argv)

    new_track = CryptoTracker()
    sendin = Sender()
    while True:
        new_vals = new_track.get_crypto_data()
        alarms_in_list = new_track.check_for_alarms(new_vals)
        if len(alarms_in_list) > 0:
            sendin.sending(alarms_in_list)
        print(f'wait {period}s')
        time.sleep(period)

