import time
import requests
import os
from twilio.rest import Client
from dotenv import load_dotenv


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
        changed_resp = self.parse_data(response.json())
        print(changed_resp)
        return changed_resp

    def parse_data(self, json_data: dict) -> dict:
        for currency in json_data:
            for coin in json_data[currency]:
                json_data[currency][coin] = round(1 / json_data[currency][coin], 5)
        return json_data

    def evaluate_data(self, json_dict: dict) -> list:
        if self.init_data is None:
            self.init_data = json_dict
            return []
        else:
            alarm_list = []
            for currency in json_dict:
                for coins in json_dict[currency]:
                    value = json_dict[currency][coins]
                    eval = self.compare(value, coins, currency)
                    if eval is not None:
                        alarm_list.append((coins, currency, value, eval[0], eval[1]))
            return alarm_list

    def compare(self, num, coin, curr):
        ref_dict = self.init_data
        ref_val = ref_dict[curr][coin]
        change = round((num - ref_val) / ref_val * 100, 3)
        if change <= - self.threshold or change >= self.threshold:
            return ref_val, change
        else:
            return None


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
        client = Client(self.account_sid_twill, self.secret_key_twill)
        for message in data_text:
            text = '\n' + '\n'.join(message)
            print(text)
            message_sent = client.messages.create(
                body=f'{text}',
                from_=f'{self.num_twill}',
                to=f'{self.user_number}'
            )
            # print(message_sent.sid)

    def process_alarm_data(self, alarms):
        # takes list of data with tuples of data for each coin:
        # crypto name, currency, current value, initial value, change %
        messages_data = []
        text_alarms = []
        length = 0
        for alarm in alarms:
            if alarm[4] < 0:
                direction = 'dropped'
            else:
                direction = 'raised'
            alarm_text = f'{alarm[0]} value {direction} by {alarm[4]}%,' \
                         f' from {alarm[3]}{alarm[1]} to {alarm[2]}{alarm[1]}'

            length += len(alarm_text) + 1  # new line counts?
            if length > self.message_lim:
                messages_data.append(text_alarms.copy())
                length = len(alarm_text) + 1
                text_alarms = []
            text_alarms.append(alarm_text)
        messages_data.append(text_alarms.copy())
        return messages_data


if __name__ == '__main__':

    new_track = CryptoTracker()
    sendin = Sender()
    while True:
        new_vals = new_track.get_crypto_data()
        alarms_in_list = new_track.evaluate_data(new_vals)
        if len(alarms_in_list) > 0:
            sendin.sending(alarms_in_list)
        print('wait 60s')
        time.sleep(60)

