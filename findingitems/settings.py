import os
import traceback
import sys
import errno
from split_settings.tools import optional, include


EXTRA_SETTINGS_DIR = '/etc/findingitems'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRA_CORE_SETTING_FILE = os.path.join(CURRENT_DIR, 'defaults.py')
EXTRA_SETTINGS_FILES = os.path.join(EXTRA_SETTINGS_DIR, '*.py')

try:
    include(EXTRA_CORE_SETTING_FILE, optional(EXTRA_SETTINGS_FILES), scope=locals())
except ImportError:
    traceback.print_exc()
    sys.exit(1)
except IOError:
    from django.core.exceptions import ImproperlyConfigured
    included_file = locals().get('__included_file__', '')
    if (not included_file or included_file == EXTRA_SETTINGS_FILES):
        # The import doesn't always give permission denied, so try to open the
        # settings file directly.
        try:
            e = None
            open(EXTRA_CORE_SETTING_FILE)
        except IOError as e:
            pass
        if e and e.errno == errno.EACCES:
            SECRET_KEY = 'permission-denied'
            LOGGING = {}
        else:
            msg = 'No nettool configuration found at %s.' % EXTRA_SETTINGS_FILES
            raise ImproperlyConfigured(msg)
    else:
        raise