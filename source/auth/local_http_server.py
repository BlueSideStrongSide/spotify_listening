from http.server import BaseHTTPRequestHandler

class MyRequestHandler(BaseHTTPRequestHandler):
    get_result = None
    def do_GET(self):
        __class__.get_result = self.path