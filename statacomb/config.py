
from argparse import ArgumentParser
from configparser import SafeConfigParser
import sys


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


def load_config(fname='config.ini'):
    config = SafeConfigParser()
    config.read(fname)
    return config


def get_settings(opts=None, config=None):
    if opts is None:
        parser = make_parser()

    if config is None:
        config = load_config()

    prefix_args = []

    for key, value in config['statacomb'].items():
        prefix_args.extend(['--%s' % key, value])

    prefix_args.extend(sys.argv[1:])

    opts = parser.parse_args(prefix_args)

    return opts
