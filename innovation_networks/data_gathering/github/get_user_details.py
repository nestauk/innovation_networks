"""Using a list of GitHub user dictionaries, get further details e.g.
followers, repos, organisations"""

import logging
import os


def get_file_path():
    """Get the path to the current file"""
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def main():
    logging.basicConfig(level=logging.DEBUG,
                        filename='/tmp/github.user_details.log')

    # Set the cwd to this file's
    os.chdir(get_file_path())

if __name__ == "__main__":
    main()
