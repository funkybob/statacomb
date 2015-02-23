
import json
import socket


class SinkHost(object):
    def __init__(self, host=None, port=None, source=None):
        self.host = host or 'localhost'
        self.port = port or 9876
        self.source = source
        self.target = (self.host, self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_data(self, values, source=None):
        source = source or self.source

        pkt = json.dumps({
            'source': source,
            'values': values,
        })
        self.socket.sendto(pkt.encode('utf-8'), self.target)
