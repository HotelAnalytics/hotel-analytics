#!/usr/bin/env python2
import logging
import argparse
import warnings
import itertools
from termcolor import colored

import appcfg

from services import TexasAPIManager, ExpediaAPIManager
from lib.utils import tojson

# {{{ Argparse setup
description = 'A tool for managing raw hotel data from external services'

# Setup argument parsing
parser = argparse.ArgumentParser(description=description)

# What app should be run
parser.add_argument(
    'app',
    nargs='?',
    default=None,
    help='The app you wish to start',
    choices=[
        'texas-api-update',
        'expedia-api-update'
    ]
)

# Optional arguments
parser.add_argument('-d', '--debug', help='Run the app in debug mode', action='store_true')
parser.add_argument('-v', '--verbose', dest='verbose', help='Make the logging verbose verbose', action='store_true')
parser.add_argument('-t', '--threads', dest='threads', default=0, help='The number of threads to run in parallel for threadable tasks', type=int)

args = parser.parse_args()
# }}}

# If an app is not specified, print instructions for how to use the tool
if not args.app:
    # {{{ Help/Info prompt
    print ''
    print colored('*' * 150, 'cyan')
    print '\t\t\tHotel Raw Data Manager - {}'.format(description)
    print colored('*' * 150 + '\n', 'cyan')

    print colored(' Usage:', 'green'), 'Pass the name of an app to', colored('start.py', 'green'), 'as the first argument. Use the', colored('--help', 'red'), 'flag for more info on flags & options.\n\n'
    print colored(' Available Apps:', 'green')
    print colored('-' * 150, 'grey')
    print colored('\ttexas-api-update                       ', 'blue'), '\tA script that consumes the data.texas.gov API for occupancy tax data'
    print colored('\texpedia-api-update                     ', 'blue'), '\tA script that consumes the expedia API for hotel metadata'
    print colored('-' * 150, 'grey')

    print '\n'
    # }}}
else:
    app_names = {
    }

    app_name = 'hotel-raw-data-manager-{}'.format(app_names[args.app] if args.app in app_names else args.app)
    logging.captureWarnings(True)
    app_logger = logging.getLogger('hotel-analytics')

    # Texas API Update
    if args.app == 'texas-api-update':
        app = TexasAPIManager(appcfg, app_logger)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')

            app.run()

    # Expedia API Update
    elif args.app == 'expedia-api-update':
        app = ExpediaAPIManager(appcfg, app_logger)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')

            app.run()
