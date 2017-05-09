#!/usr/bin/env python

from api import get_app

if __name__ == '__main__':
    get_app().run(debug=True, host="0.0.0.0", port=8000, threaded=False)
