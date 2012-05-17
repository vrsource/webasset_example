import logging
import os
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
   When complete, this filter will allow the user to filter html files into
   static output html files that include references to the Javascript and CSS
   files that should be loaded.  The goal is that when run in debug mode, this
   would reference the source js files and the uncompressed CSS files (possibly compiled).
   """
   name = 'html'

   def output(self, _in, out, **kwds):
      """ Called with concatenated inputs. """
      out.write(_in.read())

   def input(self, _in, out, **kwds):
      """ Called to filter the inputs to this filter. """
      print "WAS HERE"
      out.write(_in.read())
      # NOTE: Yet to write this code to replace with CSS and JS references
      out.write('<!-- Was Filtered -->')
      #for b in self.env:
      #   out.write('<!-- %s -->' % b.urls())

register_filter(HtmlFilter)


def out(*args):
   return pj('build', *args)


def setup_env(debug=True, cache=False):
   env = Environment(gAssetDir, gAssetUrl)

   env.debug    = debug   
   env.cache    = cache
   env.manifest = False

   # Setup Bundles
   sass = Bundle('sass/test.scss', filters='compass', output=out('css', 'test.css'),
                    debug = False)
   css  = Bundle(sass, 'style.css', output=out('css', 'min.css'))
   html = Bundle('test.html', filters='html', output=out('test.html'))
   js   = Bundle('src/test_app.js', filters='rjsmin', output=out('test_app_min.js'))

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

   print "Urls [debug]: "
   _printUrls(env)
   
   cmdenv = CommandLineEnvironment(env, log)
   cmdenv.build()

   print "Urls [prod]: "
   _printUrls(env)
      
   # Attempted another way to do this, but still can't build in debug mode
   #for b in env:
   #   b.build(force=True, env=env, disable_cache=(not cache))
   

if __name__ == '__main__':
   build()


