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
command line commands
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
        self.new_data = None

    def get_crypto_data(self):
        response = requests.get(self.crypt_endpoint)
        print(response.json())
        return response.json()

    def analyse_data(self, json_data):
        pass


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
        client = Client(self.account_sid_twill, self.secret_key_twill)
        # TODO: fix issue "HTTP 401 error: Unable to create record: Authenticate"
        message = client.messages.create(
            body=f'{data}',
            from_=f'{self.num_twill}',
            to=f'{self.user_number}'
        )
        print(message.sid)


if __name__ == '__main__':
    new_track = CryptoTracker()
    sendin = Sender()
    new_vals = new_track.get_crypto_data()
    sendin.sending(new_vals)

