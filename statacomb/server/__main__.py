
from . import SinkServer


if __name__ == '__main__':

    from statacomb import utils

    parser = utils.make_parser()

    opts = parser.parse_args()

    server = SinkServer(opts)
    server.serve_forever()
