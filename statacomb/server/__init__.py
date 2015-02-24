
import json
from socketserver import BaseRequestHandler, UDPServer

from psycopg2.extras import Json

from statacomb import utils

'''
CREATE TABLE records (
    id SERIAL,
    ts TIMESTAMP,
    source TEXT,
    src_ip INET,
    values JSON
);

CREATE INDEX records_5mins ON records (
    CAST(EXTRACT(EPOCH FROM ts) AS INT) / 300
);
CREATE INDEX records_30mins ON records (
    CAST(EXTRACT(EPOCH FROM ts) AS INT) / 1800
);

'''


class SinkHandler(BaseRequestHandler):

    def handle(self):
        try:
            data = json.loads(self.request[0].decode('utf-8'))
        except Exception:
            import traceback
            traceback.print_exc()
            return
        source = data['source']
        src_ip = self.client_address[0]
        values = data['values']

        cursor = self.server.conn.cursor()
        cursor.execute('''
            INSERT INTO records (ts, source, src_ip, values)
            VALUES ('now', %s, %s, %s)
        ''', (source, src_ip, Json(values),)
        )
        cursor.close()


class SinkServer(UDPServer):
    def __init__(self, config):

        self.conn = utils.get_db_connection(config)
        self.conn.set_session(autocommit=True)

        super().__init__((config.host, config.port), SinkHandler)
