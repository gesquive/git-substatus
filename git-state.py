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

__app__ = os.path.basename(__file__)
__author__ = "Gus Esquivel"
__copyright__ = "Copyright 2014"
__credits__ = ["Gus Esquivel"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Gus Esquivel"
__email__ = "gesquive@gmail.com"
__status__ = "Beta"


#--------------------------------------
# Configurable Constants
LOG_FILE = '/var/log/' + os.path.splitext(__app__)[0] + '.log'
LOG_SIZE = 1024*1024*200

verbose = False
debug = False

logger = logging.getLogger(__app__)

def usage():
    usage = \
"""Usage: %s [options] forced_arg
    Git utility to show the state of all subfolder git repositories
Options and arguments:
  -h --help                         Prints this message.
  -v --verbose                      Writes all messages to console.

    v%s
""" % (__app__, __version__)

    print usage


def main():
    global verbose, debug

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", \
        ["help", "verbose", "debug"])
    except getopt.GetoptError, err:
        print str(err)
        print usage()
        sys.exit(2)

    verbose = False
    debug = False
    forced_arg = None

    # Save forced arg
    if len(args) > 0:
        forced_arg = args[0]
    elif len(args) > 1:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            # Print out help and exit
            usage()
            sys.exit()
        elif o in ("-dd", "--debug"):
            debug = True
        elif o in ("-v", "--verbose"):
            verbose = True

    log_file = LOG_FILE
    if not os.access(log_file, os.W_OK):
        print "Cannot write to '%(log_file)s'.\nExiting." % locals()
        sys.exit(2)
    file_handler = logging.handlers.RotatingFileHandler(log_file,
                                            maxBytes=LOG_SIZE, backupCount=9)
    file_formater = logging.Formatter('%(asctime)s,%(levelname)s,%(thread)d,%(message)s')
    file_handler.setFormatter(file_formater)
    logger.addHandler(file_handler)

    if verbose:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter("[%(asctime)s] %(levelname)-5.5s: %(message)s")
        console_handler.setFormatter(console_formatter)
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
