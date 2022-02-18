import requests
import os
from twilio.rest import Client

"""
1. send request
2. process response json
3. evaluate state
4. send warnings if needed

Nice to add:
command line commands
ranges
higher limits
background functionality
server
"""


class CryptoTracker:
    def __int__(self):
        self.currencies = ('USD', 'EUR')
        self.crypto_api_key = '5ea05436b67f1e6902ebe83660491ac8cff0d1a94a7fea4bd66bd4936fa6f924'
        self.crypto_names = ('BTC', 'ETH', 'XRP')
        self.crypt_endpoint = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms={}&api_key={}'
        self.new_data = None

    def get_crypto_data(self):
        use_currency = ','.join(self.currencies)
        use_crypto = ','.join(self.crypto_names)
        req_url = self.crypt_endpoint.format(use_currency, use_crypto, self.crypto_api_key)
        response = requests.get(req_url)
        print(response.json())
        return response.json()

    def analyse_data(self, json_data):
        pass


class Sender:
    def __int__(self):
        self.account_sid_twill = 'AC9b68bb48726b0d5e8e3312012e4411bc'
        self.secret_key_twill = 'ebc25372f9e73878a67cced1d3cd35a8'
        self.num_twill = '+19205202812'
        self.user_number = '+37062292409'
        self.message_lim = 1600

    def send(self):
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body='Hi there',
            from_='+15017122661',
            to='+15558675310'
        )
        print(message.sid)


if __name__ == '__main__':
    new_track = CryptoTracker()
    # print(new_track.currencies)
    new_track.get_crypto_data()

