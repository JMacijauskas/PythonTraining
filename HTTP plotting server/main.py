import requests
import matplotlib
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


class Client:
    def __init__(self, name):
        self.name = name

    def send_point(self, endpoint, file):
        post_file = {'upload_file': open(file)}
        requests.post(headers={'name': self.name}, url=endpoint, files=post_file)


if __name__ == '__main__':
    client = Client('Justas')
    client.send_point('http://localhost:8000/', r'C:\Users\justas.macijauskas.QDTEAM\OneDrive - Quadigi\Documents\Python projects\PythonTraining\HTTP plotting server\README.txt')