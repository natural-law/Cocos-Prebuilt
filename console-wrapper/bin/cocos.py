#!/usr/bin/python
# ----------------------------------------------------------------------------
# cocos-console-wrapper: invoke the command line tool manager for cocos2d
#
# Author: Bill Zhang
# Copyright 2014 (C) Chukong, Inc
#
# License: MIT
# ----------------------------------------------------------------------------
'''
Invoke the command line tool cocos
'''

__docformat__ = 'restructuredtext'


# python
import sys
import os
import subprocess

def run_shell(cmd, cwd=None):
    p = subprocess.Popen(cmd, shell=True, cwd=cwd)
    p.wait()

    if p.returncode:
        raise subprocess.CalledProcessError(returncode=p.returncode, cmd=cmd)

    return p.returncode

if __name__ == "__main__":

    cur_path = os.path.realpath(os.path.dirname(__file__))
    engine_path = os.path.abspath(os.path.join(cur_path, os.path.pardir, os.path.pardir, os.path.pardir))
    console_path = os.path.abspath(os.path.join(engine_path, os.path.pardir, "cocos2d-console", "bin", "cocos"))

    args = ""
    if len(sys.argv) > 0:
        for index in range(1, len(sys.argv)):
            arg = sys.argv[index]
            if arg.find(" ") >= 0:
                arg_str = "\"%s\"" % arg
            else:
                arg_str = arg
            args += " %s" % arg_str

    if len(sys.argv) > 1 and sys.argv[1] == "new":
        args = "%s -e \"%s\"" % (args, engine_path)

    real_cmd = "%s %s" % (console_path, args)
    run_shell(real_cmd)
