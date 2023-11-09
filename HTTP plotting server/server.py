import socket

# class PlottingServer(server.HTTPServer):
#use socket

SOCKET_ADDRESS = 'localhost'
SOCKET_PORT = 7789


class SimpleServer:
    def __init__(self):
        self.socket = socket.socket()
        self.socket.bind((SOCKET_ADDRESS, SOCKET_PORT))
        self.socket.listen(5)

    def run(self):
        while True:
            # accept connections from outside
            (client_socket, address) = self.socket.accept()


if __name__ == '__main__':
    server = SimpleServer()
    server.run()
