import os
import sys

from google.appengine.ext import vendor

# Add any libraries installed in the "lib" folder.
vendor.add('lib')

if os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Engine'):
   sys.path.insert(0, 'lib.zip')
else:
    if os.name == 'nt':
        os.name = None
        sys.platform = ''

basedir = os.path.abspath(os.path.dirname(__file__))

DATA_BACKEND = 'datastore'

PROJECT_ID= 'babelli-gutenberg-copypasta'

CLOUD_STORAGE_BUCKET='babelli-epubs'


