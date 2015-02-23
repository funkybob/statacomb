
from argparse import ArgumentParser

import psycopg2


def make_parser():
    parser = ArgumentParser()
    parser.add_argument('--host', action='store', dest='host',
                        default='localhost', help='Interface to bind to')
    parser.add_argument('--port', action='store', dest='port',
                        default=9876, type=int, help='Port to bind to')

    parser.add_argument('--dbhost', action='store', dest='dbhost',
                        default=None)
    parser.add_argument('--dbport', action='store', dest='dbport',
                        default=None)
    parser.add_argument('--dbname', action='store', dest='dbname',
                        default=None)
    parser.add_argument('--dbuser', action='store', dest='dbuser',
                        default=None)
    parser.add_argument('--dbpassword', action='store', dest='dbpassword',
                        default=None)
    parser.add_argument('--dsn', action='store', dest='dsn', default=None)

    return parser


def get_db_connection(opts, **kwargs):

    return psycopg2.connect(
        dsn=opts.dsn,
        database=opts.dbname,
        user=opts.dbuser,
        password=opts.dbpassword,
        host=opts.dbhost,
        port=opts.dbport,
        **kwargs
    )
