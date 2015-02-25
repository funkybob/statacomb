
from . import SinkServer


if __name__ == '__main__':

    from statacomb import config

    opts = config.get_settings()

    server = SinkServer(opts)
    server.serve_forever()
