#!/usr/bin/env python
# git-substatus.py
# GusE 2014.12.16 V0.1
"""
Git utility to show the status of all subfolder git repositories
"""
from __future__ import print_function
__version__ = "1.3"

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
__maintainer__ = "Gus Esquivel"
__email__ = "gesquive@gmail"
__status__ = "Production"

script_www = 'https://github.com/gesquive/git-substatus'
script_url = 'https://raw.github.com/gesquive/git-substatus/master/git-substatus.py'

verbose = False
debug = False

def parse_args():
    parser = argparse.ArgumentParser(add_help=False,
        description="Git utility to show the status of all subfolder git repositories",
        epilog="%(__app__)s v%(__version__)s\n" % globals())

    group = parser.add_argument_group("Options")
    group.add_argument("-d", "--dir", default=".",
        help="The parent directory to the git repositories.")
    group.add_argument("-a", "--list-all", action="store_true",
        help="List all directories.")
    group.add_argument("-n", "--list-others", action="store_true",
        help="List only non-git directories.")
    group.add_argument("-R", "--reverse-sort", action="store_true",
        help="Reverse the order of the listed repositories.")
    group.add_argument("-h", "--help", action="help",
        help="Show this help message and exit.")
    group.add_argument("-v", "--verbose", action="store_true", dest="verbose",
        help="Writes all messages to console.")
    group.add_argument("-D", "--debug", action="store_true", dest="debug",
        help=argparse.SUPPRESS)
    group.add_argument("-u", "--update", action="store_true", dest="update",
        help="Checks server for an update, replaces the current version if "\
        "there is a newer version available.")
    group.add_argument("-V", "--version", action="version",
                    version="%(__app__)s v%(__version__)s" % globals())

    args = parser.parse_args()
    return args


def init_logging(verbose, debug):
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter("")
    console_handler.setFormatter(console_formatter)
    logging.getLogger('').addHandler(console_handler)

    if verbose or debug:
        logging.getLogger('').setLevel(logging.DEBUG)
        logging.debug("Verbose mode activated.")
    else:
        logging.getLogger('').setLevel(logging.INFO)


def main():
    global verbose, debug
    args = parse_args()

    verbose = args.verbose
    debug = args.debug

    init_logging(verbose, debug)

    if args.update:
        update(script_url)
        sys.exit()

    colors.init()

    try:
        dir_infos = get_dir_info(args.dir, args.reverse_sort)
        output = ['Status of "{}"'.format(os.path.abspath(args.dir))]
        for dir_info in dir_infos:
            if args.list_all or\
               (args.list_others and not dir_info['is_git_repo']) or\
               (not args.list_others and dir_info['is_git_repo']):
                output.append(get_pretty_out(dir_info))
        output_to_pager(output)
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception:
        logging.exception("Fatal error")


from glob import glob
def get_dir_info(parent_dir, reverse=False):
    dir_info = []
    if os.path.exists(os.path.join(parent_dir, '.git')):
        dir_info.append(get_git_info(parent_dir))
    else:
        for sub_dir in glob(os.path.join(parent_dir, '*')):
            if os.path.isdir(sub_dir):
                dir_info.append(get_git_info(sub_dir))
    dir_info.sort(key=lambda d: d['name'].lower(), reverse=reverse)
    return dir_info


def get_git_info(dir_path):
    dir_info = {}
    dir_info['name'] = os.path.basename(os.path.abspath(dir_path))
    is_git_repo = os.path.exists(os.path.join(dir_path, '.git'))
    dir_info['is_git_repo'] = is_git_repo

    branch_regex = re.compile(r'.*On branch (?P<branch>.*)')
    if is_git_repo:
        git_status = sh('git status', cwd=dir_path)
        results = re.match(branch_regex, git_status)
        if results:
            (branch_name,) = results.groups(0)
            dir_info['branch_name'] = branch_name
        else:
            dir_info['branch_name'] = 'none'

        dir_info['has_changes'] = git_status.find('nothing to commit') == -1
    return dir_info

def get_pretty_out(dir_info, name_length=50):
    if len(dir_info['name']) > name_length:
        pretty_name = '{}...'.format(dir_info['name'][:name_length-3])
    else:
        pretty_name = dir_info['name']
    if dir_info['is_git_repo']:
        dir_color = colors.BLUE
        branch_color = colors.PURPLE
        if dir_info['branch_name'] == 'master':
            branch_color = colors.GREEN

        git_status = 'no changes'
        status_color = colors.GREEN
        if dir_info['has_changes']:
            git_status = 'changes'
            status_color = colors.RED
        branch_name = dir_info['branch_name']
    else:
        dir_color = colors.GREY
        branch_color = colors.YELLOW
        branch_name = 'no git'
        status_color = colors.RED
        git_status = ''

    name_spacing = '-' * ((name_length+14)-(len(pretty_name)+len(branch_name)))

    status_line = '{}{}{} {}{}{} {}{}{} : {}{:<10}{}'.format(
        dir_color, pretty_name, colors.RESET,
        colors.GREY, name_spacing, colors.RESET,
        branch_color, branch_name, colors.RESET,
        status_color, git_status, colors.RESET)

    return status_line


def sh(command, cwd=None, seperate=True):
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
            pager.stdin.write("{}{}".format(line, os.linesep))
        pager.stdin.close()
        pager.wait()
    except KeyboardInterrupt:
        pass
        # let less handle this, -K will exit cleanly


def update(dl_url, force_update=False):
    """
Attempts to download the update url in order to find if an update is needed.
If an update is needed, the current script is backed up and the update is
saved in its place.
"""
    import urllib
    import re
    from subprocess import call
    def compare_versions(vA, vB):
        """
Compares two version number strings
@param vA: first version string to compare
@param vB: second version string to compare
@author <a href="http_stream://sebthom.de/136-comparing-version-numbers-in-jython-pytho/">Sebastian Thomschke</a>
@return negative if vA < vB, zero if vA == vB, positive if vA > vB.
"""
        if vA == vB: return 0

        def num(s):
            if s.isdigit(): return int(s)
            return s

        seqA = map(num, re.findall('\d+|\w+', vA.replace('-SNAPSHOT', '')))
        seqB = map(num, re.findall('\d+|\w+', vB.replace('-SNAPSHOT', '')))

        # this is to ensure that 1.0 == 1.0.0 in cmp(..)
        lenA, lenB = len(seqA), len(seqB)
        for i in range(lenA, lenB): seqA += (0,)
        for i in range(lenB, lenA): seqB += (0,)

        rc = cmp(seqA, seqB)

        if rc == 0:
            if vA.endswith('-SNAPSHOT'): return -1
            if vB.endswith('-SNAPSHOT'): return 1
        return rc

    # dl the first 256 bytes and parse it for version number
    try:
        logging.info("Checking the latest version...")
        http_stream = urllib.urlopen(dl_url)
        update_file = http_stream.read(256)
        http_stream.close()
    except IOError, (errno, strerror):
        logging.exception("Unable to retrieve version data")
        return

    match_regex = re.search(r'__version__ *= *"(\S+)"', update_file)
    if not match_regex:
        logging.error("No version info could be found")
        return
    update_version = match_regex.group(1)

    if not update_version:
        logging.error("Unable to parse version data")
        return

    if force_update:
        logging.info("Forcing update, downloading version {}..."
                     "".format(update_version))
    else:
        cmp_result = compare_versions(__version__, update_version)
        if cmp_result < 0:
            logging.info("Newer version ({}) available, downloading..."
                         "".format(update_version))
        elif cmp_result > 0:
            logging.info("Local version ({}) is newer then available ({}), "
                         "not updating.".format(__version__, update_version))
            return
        else:
            logging.info("You already have the latest version.")
            return

    # dl, backup, and save the updated script
    app_path = os.path.realpath(sys.argv[0])

    if not os.access(app_path, os.W_OK):
        logging.error("Cannot update -- unable to write to {}".format(app_path))

    dl_path = app_path + ".new"
    backup_path = app_path + ".old"
    try:
        dl_file = open(dl_path, 'w')
        http_stream = urllib.urlopen(dl_url)
        total_size = None
        bytes_so_far = 0
        chunk_size = 8192
        try:
            total_size = int(http_stream.info().getheader('Content-Length').strip())
        except:
            # The header is improper or missing Content-Length, just download
            dl_file.write(http_stream.read())

        while total_size:
            chunk = http_stream.read(chunk_size)
            dl_file.write(chunk)
            bytes_so_far += len(chunk)

            if not chunk:
                break

            percent = float(bytes_so_far) / total_size
            percent = round(percent*100, 2)
            sys.stdout.write("Downloaded {} of {} bytes ({:0.2f})\r"
                             "".format(bytes_so_far, total_size, percent))

            if bytes_so_far >= total_size:
                sys.stdout.write('\n')

        http_stream.close()
        dl_file.close()
    except IOError, (errno, strerror):
        logging.exception("Download failed")
        return

    try:
        os.rename(app_path, backup_path)
    except OSError, (errno, strerror):
        logging.exception()("Unable to rename {} to {}: ({}) {}"
                            "".format(app_path, backup_path, errno, strerror))
        return

    try:
        os.rename(dl_path, app_path)
    except OSError, (errno, strerror):
        logging.exception("Unable to rename {} to {}: ({}) {}"
                          "".format(dl_path, app_path, errno, strerror))
        return

    try:
        import shutil
        shutil.copymode(backup_path, app_path)
    except:
        pass
        os.chmod(app_path, 0755)

    logging.info("New version installed as {}".format(app_path))
    logging.info("(previous version backed up to {})".format(backup_path))
    return


class colors:
    BLACK = ''
    RED = ''
    GREEN = ''
    YELLOW = ''
    BLUE = ''
    PURPLE = ''
    CYAN = ''
    WHITE = ''
    GREY = ''
    END = ''

    @staticmethod
    def init():
        if colors.supports_color():
            colors.BLACK = '\033[30m'
            colors.RED = '\033[31m'
            colors.GREEN = '\033[32m'
            colors.YELLOW = '\033[33m'
            colors.BLUE = '\033[34m'
            colors.PURPLE = '\033[35m'
            colors.CYAN = '\033[36m'
            colors.WHITE = '\033[1;37m'
            colors.GREY = '\033[0;37m'
            colors.RESET = '\033[0m'

    @staticmethod
    def blue(msg):
        return '{}{}{}'.format(colors.BLUE, msg, colors.RESET)
    @staticmethod
    def green(msg):
        return '{}{}{}'.format(colors.GREEN, msg, colors.RESET)
    @staticmethod
    def yellow(msg):
        return '{}{}{}'.format(colors.YELLOW, msg, colors.RESET)
    @staticmethod
    def red(msg):
        return '{}{}{}'.format(colors.RED, msg, colors.RESET)

    @staticmethod
    def supports_color():
        """
        Returns True if the running system's terminal supports color, and False
        otherwise.
        """
        plat = sys.platform
        supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                      'ANSICON' in os.environ)
        # isatty is not always implemented, #6223.
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        if not supported_platform or not is_a_tty:
            return False
        return True


if __name__ == '__main__':
    main()
