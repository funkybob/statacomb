
from antfarm import App

from gunicorn.app.base import BaseApplication

from . import connect

#  http://docs.gunicorn.org/en/latest/custom.html


class StatacombApplication(BaseApplication):

    def __init__(self, opts, config):
        self.options = opts
        self.config = config
        super().__init__()

    def load_config(self):
        for key, value in self.config.items():
            self.cfg.set(key, value)

    def load(self):
        return App(root_view=connect, config=self.options)


if __name__ == '__main__':
    from statacomb import config

    cfg = config.load_config()
    opts = config.get_settings(config=cfg)

    StatacombApplication(opts, cfg['gunicorn']).run()
