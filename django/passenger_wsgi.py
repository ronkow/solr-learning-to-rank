"""
SET THESE 3 LINES:
import grammar.wsgi
SCRIPT_NAME = '/my_path/'
application = grammar.wsgi.application
"""

import os
import sys

sys.path.append(os.getcwd())

os.environ['DJANGO_SETTINGS_MODULE'] = 'grammar.settings'

import grammar.wsgi
from whitenoise import WhiteNoise

SCRIPT_NAME = os.getcwd()
SCRIPT_NAME = ''

class PassengerPathInfoFix(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        from urllib.parse import unquote
        environ['SCRIPT_NAME'] = SCRIPT_NAME

        request_uri = unquote(environ['REQUEST_URI'])
        script_name = unquote(environ.get('SCRIPT_NAME', ''))
        offset = request_uri.startswith(script_name) and len(environ['SCRIPT_NAME']) or 0
        environ['PATH_INFO'] = request_uri[offset:].split('?', 1)[0]

        return self.app(environ, start_response)

application = grammar.wsgi.application
application = PassengerPathInfoFix(application)
application = WhiteNoise(application, root='/my_path/static_files')
