import os
import time
import logging
import traceback
import requests
import multiprocessing
import math
import Queue
from copy import deepcopy
from sqlalchemy import create_engine, not_
from sqlalchemy.orm import sessionmaker
from elasticsearch import Elasticsearch, helpers, ConnectionTimeout, SerializationError
from dateutil.parser import parse
from datetime import datetime

from lib.utils import tryparseint, tryparsefloat, parsedate, parsedatetime, get_quarter, get_previous_quarter

script_path = os.path.dirname(os.path.abspath(__file__))

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

class TexasAPIManager():
    def __init__(self, config=None, debug=False):
        self.config = config
        self.logger = logging.getLogger('hotel-analytics')
        self.debug = debug

        # Set up the PostgreSQL db session
        self.pg_engine = create_engine(config.POSTGRES_URI)
        Session = sessionmaker(bind=self.pg_engine)
        self.db = Session()

        self.socrata_headers = {'X-App-Token': config.SOCRATA_APP_TOKEN}

        self.page_size = config.API_PAGE_SIZE

    # {{{ run
    def run(self, threads=None):
        self.logger.info('Running Texas API importer')

        start_time = time.time()

        # Run logic here

        self.logger.info('Finished importing from data.texas.gov: {} sec'.format(time.time() - start_time))
    # }}}
