import multiprocessing
from types import MethodType

from http.server import BaseHTTPRequestHandler, HTTPServer as _HTTPServer

class HTTPServer(_HTTPServer):
    def serve_forever(self):
        host, port = self.server_address
        print(f'Server started listening on http://{host}:{port}\n')
        try:
            super().serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            super().server_close()
            print('\nServer stopped.')


class EchoHTTPRequestHandler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        
        self._response = []
        
        handler = self
        old_write = self.wfile.write

        def _write(self, b):
            handler._response.append(b)
            old_write(b)
                
        self.wfile.write = MethodType(_write, self.wfile)
        
    def __getattr__(self, name):
        # handle_one_request calls do_[METHOD] to handle requests that has [METHOD]
        # this ensures all the requests are logged and handled by `handle_request`
        # I did that for educational purpouses, I want my students to understand that [METHOD]
        # is an arbitrary string and 'GET', 'POST' ... are just conventions, well I'm not even sure about that LooL
        if name.startswith('do_'):
            return self._do_every_command
        else:
            return super().__getattr(name)

        
    def print_request(self):
        print(self.requestline)
        
        # Headers
        print()
        for header, value in self.headers.items():
            print(f'{header}: {value}')

        # Data
        content_length = int(self.headers.get('Content-Length', 0))
        content = self.rfile.read(content_length).decode()
        if content:
            print()
            print(content)
        
    def print_response(self):
        response = ''.join([line.decode() for line in self._response])
        print(response)
    
    def _do_every_command(self):
        print('########## HTTP Request  ##########')
        self.print_request()
        print('########## HTTP Request  ##########')

        self.handle_request()
        
        print('########## HTTP Response ##########')
        self.print_response()
        print('########## HTTP Response ##########')
        
        self._response = []
        