
from sanic import Sanic

app = Sanic()
import server.config

app.config.from_object(server.config)

import server.views
 