#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2022 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

"""
    File Server
    ~~~~~~~~~~~

    DIM network supporting service
"""

import sys

from dimples.utils import SysArgvParser
from dimples.utils import init_logger
from dimples.utils import LogLevel
from dimples.utils import Runner
from dimples.utils import Path

path = Path.abs(path=__file__)
path = Path.dir(path=path)
path = Path.dir(path=path)
Path.add(path=path)

from server.shared import GlobalVariable
from server.shared import create_config
from server.cleaner import FileCleaner
from server.handler import app


#
#  show logs
#
LOG_LEVEL = LogLevel.DEVELOP
LOGGER_NAME = 'ftp'

APP_NAME = 'File Server'

DEFAULT_CONFIG = '/etc/dim/ftp.ini'


def show_help():
    cmd = sys.argv[0]
    print('')
    print('    %s' % APP_NAME)
    print('')
    print('usages:')
    print('    %s [--config=<FILE>]' % cmd)
    print('    %s [-h|--help]' % cmd)
    print('')
    print('optional arguments:')
    print('    --config        config file path (default: "%s")' % DEFAULT_CONFIG)
    print('    --help, -h      show this help message and exit')
    print('')


async def async_main():
    #
    #  parse cmd parameters
    #
    sys_argv = SysArgvParser.parse(shortopts='hf:ld:',
                                   longopts=['help', 'config=', 'log-location', 'log-dir='])
    if sys_argv is None:
        show_help()
        sys.exit(1)
    #
    #  init logger
    #
    show_location = sys_argv.has_opt(opt='log-location')
    init_logger(name=LOGGER_NAME, level=LOG_LEVEL, show_location=show_location)
    #
    #  create config
    #
    config = await create_config(sys_argv=sys_argv, default_config=DEFAULT_CONFIG)
    if config is None:
        show_help()
        sys.exit(1)
    #
    #  Start cleaner
    #
    shared = GlobalVariable()
    cleaner = FileCleaner()
    cleaner.root = shared.upload_directory
    #
    #  Start server
    #
    host = shared.server_host
    port = shared.server_port
    # app.run(host=host, port=port, debug=True)
    app.run(host=host, port=port)


def main():
    Runner.sync_run(main=async_main())


if __name__ == '__main__':
    main()
