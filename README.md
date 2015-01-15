##git-substatus

List the short status of all subdirectory git repositories.

```
usage: git-substatus.py [-d DIR] [-h] [-v] [-V]

Git utility to show the status of all subfolder git repositories

Options:
  -d DIR, --dir DIR  The parent directory to the git repositories.
  -h, --help         Show this help message and exit.
  -v, --verbose      Writes all messages to console.
  -V, --version      show program's version number and exit
  ```

### Installation Instructions

Run the following command:
```
SDIR=/usr/local/bin/; wget https://raw.github.com/gesquive/git-substatus/master/git-substatus.py -O ${SDIR}/git-substatus && chmod +x ${SDIR}/git-substatus
```

If you wish to install to a different directory just change the `SDIR` value.
Keep in mind, if you want to be able to run the script as a git sub-command (ie. run as `git status`) you must make the script executable and available on the `$PATH`