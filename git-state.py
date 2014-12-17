#!/usr/bin/env python
# git-state.py
# GusE 2014.12.16 V0.1
"""
Git utility to show the state of all subfolder git repositories
"""

import getopt
import sys
import os
import subprocess
import traceback
import logging
import logging.handlers
import argparse

__app__ = os.path.basename(__file__)
__author__ = "Gus Esquivel"
__copyright__ = "Copyright 2014"
__credits__ = ["Gus Esquivel"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Gus Esquivel"
__email__ = "gesquive@gmail"
__status__ = "Beta"


#--------------------------------------
# Configurable Constants
LOG_FILE = '/var/log/' + os.path.splitext(__app__)[0] + '.log'
LOG_SIZE = 1024*1024*200

verbose = False
debug = False

logger = logging.getLogger(__app__)

def main():
    global verbose, debug

    parser = argparse.ArgumentParser(add_help=False,
        description="Git utility to show the state of all subfolder git repositories",
        epilog="%(__app__)s v%(__version__)s\n" % globals())

    group = parser.add_argument_group("Options")
    group.add_argument("-d", "--dir", default=".",
        help="The parent directory to the git repositories.")
    group.add_argument("-h", "--help", action="help",
        help="Show this help message and exit.")
    group.add_argument("-v", "--verbose", action="store_true", dest="verbose",
        help="Writes all messages to console.")
    group.add_argument("-D", "--debug", action="store_true", dest="debug",
        help=argparse.SUPPRESS)
    group.add_argument("-V", "--version", action="version",
                    version="%(__app__)s v%(__version__)s" % globals())

    args = parser.parse_args()
    verbose = args.verbose
    debug = args.debug

    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter("[%(asctime)s] %(levelname)-5.5s: %(message)s")
    console_handler.setFormatter(console_formatter)
    if verbose:
        logger.addHandler(console_handler)

    logger.setLevel(logging.DEBUG)

    try:
        # DO SOMETHING
        do_something()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception, e:
        print traceback.format_exc()


def do_something():
    print "Hello World!"

if __name__ == '__main__':
    main()
