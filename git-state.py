#!/usr/bin/env python
# git-state.py
# GusE 2014.12.16 V0.1
"""
Git utility to show the state of all subfolder git repositories
"""

from __future__ import print_function

import getopt
import sys
import os
import subprocess
import traceback
import logging
import logging.handlers
import argparse
import re

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


class colors:
    PRE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'


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
        git_dirs = get_get_dirs(args.dir)
        if len(git_dirs) == 0:
            logger.error("None of the subdirectories have git repositories.")
        for git_dir in git_dirs:
            print_git_status(git_dir)
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception:
        print(traceback.format_exc())


from glob import glob


def get_get_dirs(parent_dir):
    git_dirs = []
    for sub_file in glob(os.path.join(parent_dir, '*')):
        if os.path.exists(os.path.join(sub_file, ".git")):
            git_dirs.append(sub_file)
    return git_dirs


branch_regex = re.compile(r'.*On branch (?P<branch>.*)')

def print_git_status(git_dir):
    saved_cwd = os.getcwd()
    # print("Checking for status in {}".format(git_dir))
    git_dir = os.path.abspath(git_dir)
    os.chdir(git_dir)
    status_out = popen("git status")
    # print (status_out)

    # start = status_out.find("On branch")
    # end = status_out.find('\n', start)
    # branch = status_out
    results = re.match(branch_regex, status_out)
    if results:
        (branch_name,) = results.groups(0)

    git_status = "Changes"
    if status_out.find('nothing to commit') != -1:
        git_status = "No Changes"

    pretty_git_name = os.path.basename(git_dir)
    print("{} {} {}".format(pretty_git_name, branch_name, git_status))

    os.chdir(saved_cwd)


def popen(command, cwd=None, seperate=True):
    """
    Returns the stdout from the given command, using the subprocess
    command.
    """
    cmd = subprocess.Popen(command, shell=seperate, stdout=subprocess.PIPE,
                           cwd=cwd)
    res = cmd.stdout.read()
    cmd.wait()
    return res


def output_to_pager(text):
    try:
        # args stolen fron git source, see `man less`
        pager = subprocess.Popen(['less', '-F', '-R', '-S', '-X', '-K'],
                                 stdin=subprocess.PIPE,
                                 stdout=sys.stdout)
        for line in text:
            pager.write(line)
        pager.stdin.close()
        pager.wait()
    except KeyboardInterrupt:
        pass
        # let less handle this, -K will exit cleanly

if __name__ == '__main__':
    main()
