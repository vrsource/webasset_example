import logging
import os
import re
import sys

pj = os.path.join

# Setup the paths to the dependencies
file_dir  = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, pj(file_dir, 'webassets', 'src'))

from webassets        import Environment, Bundle
from webassets.script import CommandLineEnvironment
from webassets.filter import Filter, register_filter

gAssetDir = os.path.abspath(pj(file_dir, 'static'))
gAssetUrl = '/static'


class HtmlFilter(Filter):
   """
   his filter allows the user to filter html files into static output html files
   that include references to the Javascript and CSS files that should be loaded.
   The goal is that when run in debug mode, this would reference the source js files
   and the uncompressed CSS files (possibly compiled).

   Looks for the following TAGS in the html file:
     * {{CSS_LINKS}}: Replaced with <link> elements to each css file
     * {{JS_LINKS}}: Replaced with <script> elements to each js file.
   """
   name = 'html'

   def __init__(self, css = None, js = None, *a, **kw):
      self.css = css or []
      self.js  = js  or []
      super(HtmlFilter, self).__init__(*a, **kw)

   def output(self, _in, out, **kwds):
      """ Called with concatenated inputs. """
      out.write(_in.read())

   def input(self, _in, out, **kwds):
      """ Called to filter the inputs to this filter. """
      content = _in.read()

      # Build up content to replace
      css_code = ''
      js_code  = ''

      for css_name in self.css:
         for url in self.env[css_name].urls():
            css_code += '<link rel="stylesheet" href="%s" type="text/css"/>\n' % url

      for js_name in self.js:
         for url in self.env[js_name].urls():
            js_code += '<script type="text/javascript" src="%s"></script>\n' % url

      content = re.sub("{{\s*?JS_LINKS\s*?}}", js_code, content)
      content = re.sub("{{\s*?CSS_LINKS\s*?}}", css_code, content)

      out.write(content)


register_filter(HtmlFilter)


def out(*args):
   return pj('build', *args)

def html_filter(css, js):
   return HtmlFilter(css=css, js=js)

def setup_env(debug=True, cache=False):
   env = Environment(gAssetDir, gAssetUrl)

   env.debug    = debug
   env.cache    = cache
   env.manifest = False

   # Setup Bundles
   sass = Bundle('sass/test.scss', filters='compass', output=out('css', 'test.css'),
                    debug = False)
   css  = Bundle(sass, 'style.css', output=out('css', 'min.css'))
   js   = Bundle('src/test_app.js', filters='rjsmin', output=out('test_app_min.js'))
   html = Bundle('test.html', output=out('test.html'),
                 filters = html_filter(css=['css'], js=['js']))

   # Register bundles
   env.register('css',  css)
   env.register('html', html)
   env.register('js',   js)

   return env


def load_logger():
   # Setup a logger
   log = logging.getLogger('webassets')
   log.addHandler(logging.StreamHandler())
   log.setLevel(logging.DEBUG)
   return log

def _printUrls(env):
   for b in env:
      print b.urls()

def build():
   env = setup_env()
   log = load_logger()

   print "Urls [before build]: "
   _printUrls(env)

   cmdenv = CommandLineEnvironment(env, log)
   cmdenv.build()

   print "Urls [after build]: "
   _printUrls(env)

   # Attempted another way to do this, but still can't build in debug mode
   #for b in env:
   #   b.build(force=True, env=env, disable_cache=(not cache))


if __name__ == '__main__':
   build()


