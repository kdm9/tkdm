# Copyright (c) 2022 Dr. K. D. Murray/Gekkonid Consulting <spam@gekkonid.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from sys import argv, exit, stderr
__version__ = "0.1.0"

cmds = {}

try:
    from .autogallery import main as autogallery_main
    cmds["autogallery"] = autogallery_main
except ImportError:
    pass
try:
    from .genautoindex import main as genautoindex_main
    cmds["genautoindex"] = genautoindex_main
except ImportError:
    pass


def mainhelp(argv=None):
    """Print this help message"""
    print("USAGE: tkdm <subtool> [options...]\n\n")
    print("Where <subtool> is one of:\n")
    for tool, func in cmds.items():
        print("  {:<19}".format(tool + ":"), " ", func.__doc__.split("\n")[0])
    print("\n\nUse tkdm subtool --help to get help about a specific tool")

cmds["help"] = mainhelp

def main():
    if len(argv) < 2:
        mainhelp()
        exit(0)
    if argv[1] not in cmds:
        print("ERROR:", argv[1], "is not a known subtool. See help below")
        mainhelp()
        exit(1)
    cmds[argv[1]](argv[2:])

