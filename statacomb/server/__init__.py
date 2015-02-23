
import json
from socketserver import BaseRequestHandler, UDPServer

from psycopg2.extras import Json

'''
CREATE TABLE records (
    id SERIAL,
    ts TIMESTAMP,
    source TEXT,
    src_ip INET,
    values JSON
);
CREATE INDEX records_5mins ON records (
    CAST( (EXTRACT(EPOCH FROM ts) / 300) AS INT)
);
CREATE INDEX records_30mins ON records (
    CAST( (EXTRACT(EPOCH FROM ts) / 1800) AS INT)
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

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO records (ts, source, src_ip, values)
            VALUES ('now', %s, %s, %s)
        ''', (source, src_ip, Json(values),)
        )
        cursor.close()


if __name__ == '__main__':

    from statacomb import utils

    parser = utils.make_parser()

    opts = parser.parse_args()

    conn = utils.get_db_connection(opts)
    conn.set_session(autocommit=True)

    server = UDPServer((opts.host, opts.port), SinkHandler)
    server.serve_forever()
