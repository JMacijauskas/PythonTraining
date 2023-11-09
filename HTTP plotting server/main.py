import random
import requests

"""
run HTTP server (socket)
each user sends point to extend graph
use matplotlib for displaying data
have queue for multiple clients to display data one after other
display time duration, if queue exists?
display in tkinter? or web
identifier?
constantly update display for users?
"""

"""
User POST coordinate -> server -> Queue -> parse coordinate -> add to plot -> display in main view
"""

COORD_RANGE = (-100, 100)


def coordinate_generator():
    return {'x': random.randint(*COORD_RANGE), 'y': random.randint(*COORD_RANGE)}


class Client:
    def __init__(self, name):
        self.name = name

    def send_point(self, endpoint: str | bytes) -> None:
        post_coord = coordinate_generator()
        requests.post(headers={'name': self.name}, url=endpoint, data=post_coord)


if __name__ == '__main__':
    client = Client('Justas')
    client.send_point('http://localhost:7789')
    client2 = Client('Justas2')
    client2.send_point('http://localhost:7789')
