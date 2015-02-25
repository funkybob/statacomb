
from antfarm import App

from . import connect

opts = config.get_settings()

application = App(root_view=connect, config=opts)
