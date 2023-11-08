from http import server

# class PlottingServer(server.HTTPServer):
#use socket


class MultiCallHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.responses)
        print(self.request)

    def do_POST(self):
        print(self.responses)
        print(self.request)


def run(server_class=server.ThreadingHTTPServer, handler_class=MultiCallHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
    run()