from jinja2 import Template
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from bokeh.embed import autoload_static
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.sampledata.penguins import data
from bokeh.util.browser import view

template = Template("""
<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">
</head>

<body>
  <div>
    The plot embedded below is a standalone plot that was embedded using
    <fixed>autoload_static</fixed>. For more information see the
    <a target="_blank" href="https://docs.bokeh.org/en/latest/docs/user_guide/embed.html#autoload-scripts">
    documentation</a>.
  </div>
  {{ script|safe }}
</body>
</html>
""")


class IndexHandler(RequestHandler):
    def initialize(self, script):
        self.script = script

    def get(self):
        self.write(template.render(script=self.script))


# Normally, you might save the .js files to some location on disk, and serve
# them from there. Here we use this request handler, just to make the example
# completely self-contained.
class JSHandler(RequestHandler):
    def initialize(self, js):
        self.js = js

    def get(self):
        self.write(self.js)


def make_plot():
    colormap = {'Adelie': 'red', 'Chinstrap': 'green', 'Gentoo': 'blue'}
    colors = [colormap[x] for x in data['species']]

    p = figure(title="Penguin size")
    p.xaxis.axis_label = "Bill Length (mm)"
    p.yaxis.axis_label = "Body Mass (g)"

    p.scatter(data["bill_length_mm"], data["body_mass_g"],
              color=colors, fill_alpha=0.2, size=10)

    return p


if __name__ == '__main__':
    print('Opening Tornado app with embedded Bokeh plot on http://localhost:8080/')

    js, script = autoload_static(make_plot(), CDN, "embed.js")

    app = Application([
        (r"/", IndexHandler, dict(script=script)),
        (r"/embed.js", JSHandler, dict(js=js)),
    ])
    app.listen(8080)

    io_loop = IOLoop.current()
    io_loop.add_callback(view, "http://localhost:8080/")
    io_loop.start()
