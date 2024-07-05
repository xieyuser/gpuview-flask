#!/usr/bin/env python

"""
Web API of gpuview.

@author Fitsum Gaim
@change Bei9
@url https://github.com/fgaim
"""

import os
import json
from datetime import datetime

# from bottle import Bottle, TEMPLATE_PATH, template, response, static_file
from flask import Flask, jsonify, render_template, send_file
from flask_caching import Cache

from . import utils
from . import core


app = Flask(__name__, template_folder='views')
cache = Cache(app, config={'CACHE_TYPE': 'simple'})  # 使用 simple 缓存类型

EXCLUDE_SELF = False  # Do not report to `/gpustat` calls.


@app.route('/')
@app.route('/index')
def index():
    return send_file('views/index.html')

@app.route('/test')
def index_test():
    gpustats = core.all_gpustats()
    now = datetime.now().strftime('Updated at %Y-%m-%d %H-%M-%S')
    return render_template('index.tpl', gpustats=gpustats, update_time=now)

@app.route('/gpustat', methods=['GET'])
def report_gpustat():
    """
    Returns the gpustat of this host.
        See `exclude-self` option of `gpuview run`.
    """
    response = core.my_gpustat()
    return jsonify(response)


@app.route('/all_gpustat', methods=['GET'])
@cache.cached(timeout=2) 
def report_all_gpustat():
    gpustats = core.all_gpustats()
    now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    return jsonify({'gpustats': gpustats, 'now': now})



def main():
    parser = utils.arg_parser()
    args = parser.parse_args()

    if 'run' == args.action:
        core.safe_zone(args.safe_zone)
        global EXCLUDE_SELF
        EXCLUDE_SELF = args.exclude_self
        app.run(host=args.host, port=args.port, debug=args.debug)
    elif 'service' == args.action:
        core.install_service(host=args.host,
                             port=args.port,
                             safe_zone=args.safe_zone,
                             exclude_self=args.exclude_self)
    elif 'add' == args.action:
        core.add_host(args.url, args.name)
    elif 'remove' == args.action:
        core.remove_host(args.url)
    elif 'hosts' == args.action:
        core.print_hosts()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
