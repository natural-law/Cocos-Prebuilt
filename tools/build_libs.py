#!/usr/bin/python
# ----------------------------------------------------------------------------
# build libs
#
# Copyright 2014 (C) zhangbin
#
# License: MIT
# ----------------------------------------------------------------------------
'''
Build the libs project of engine
'''

import os
import subprocess
import shutil
import excopy

XCODE_PROJ_INFO = {
    "cocos2d-x/build/cocos2d_libs.xcodeproj" : [ "build all libs" ],
    "cocos2d-x/cocos/scripting/lua-bindings/proj.ios_mac/cocos2d_lua_bindings.xcodeproj" : [ "luabindings" ]
}

X_IOS_OUTPUT_DIR = "gen/cocos2d-x/prebuilt/ios"
X_MAC_OUTPUT_DIR = "gen/cocos2d-x/prebuilt/mac"
X_COPY_CONFIG = [
    {
        "from": "cocos2d-x",
        "to": "gen/cocos2d-x",
        "include": [
            "cocos/*.h$",
            "cocos/math/*.inl$",
            "extensions/*.h$",
            "external/*.h$"
        ]
    },
    {
        "from": "cocos2d-x/cocos/platform/android/java",
        "to": "gen/cocos2d-x/cocos/platform/android/java"
    },
    {
        "from": "cocos2d-x/cocos/scripting/lua-bindings/script",
        "to": "gen/cocos2d-x/cocos/scripting/lua-bindings/script"
    },
    {
        "from": "cocos2d-x/templates",
        "to": "gen/cocos2d-x/templates",
        "exclude" : [
            "cpp-template-default/*",
            "lua-template-runtime/*"
        ]
    },
    {
        "from": "cocos2d-x/tools/cocos2d-console",
        "to": "gen/cocos2d-x/tools/cocos2d-console"
    },
    {
        "from": "x-templates",
        "to": "gen/cocos2d-x/templates"
    }
]

def run_shell(cmd, cwd=None):
    """
    Runs shell command.

    @type cmd:  string
    @param cmd: Command to be executed.

    @type cwd:  string
    @param cwd: Working directory.

    @rtype:     int
    @return:    Return code of the command.

    @raise CalledProcessError:  Raises exception if return code of the command is non-zero.
    """
    p = subprocess.Popen(cmd, shell=True, cwd=cwd)
    p.wait()

    if p.returncode:
        raise subprocess.CalledProcessError(returncode=p.returncode, cmd=cmd)

    return p.returncode

class LibsBuilder(object):

    IOS_CMD_FMT = "xcodebuild -project \"%s\" -configuration Release -target \"%s iOS\" -sdk %s CONFIGURATION_BUILD_DIR=%s"
    MAC_CMD_FMT = "xcodebuild -project \"%s\" -configuration Release -target \"%s Mac\" CONFIGURATION_BUILD_DIR=%s"

    def __init__(self):
        self.tool_dir = os.path.realpath(os.path.dirname(__file__))
        self.root_dir = os.path.join(self.tool_dir, os.path.pardir)

    def copy_files(self):
        for cfg in X_COPY_CONFIG:
            excopy.copy_files_with_config(cfg, self.root_dir, self.root_dir)

    def build_ios_mac(self):
        x_ios_out_dir = os.path.join(self.root_dir, X_IOS_OUTPUT_DIR)
        x_mac_out_dir = os.path.join(self.root_dir, X_MAC_OUTPUT_DIR)
        for key in XCODE_PROJ_INFO.keys():
            proj_path = os.path.join(self.root_dir, key)
            for target in XCODE_PROJ_INFO[key]:
                build_cmd = LibsBuilder.IOS_CMD_FMT % (proj_path, target, "iphonesimulator", os.path.join(x_ios_out_dir, "simulator"))
                run_shell(build_cmd, self.tool_dir)

                build_cmd = LibsBuilder.IOS_CMD_FMT % (proj_path, target, "iphoneos", os.path.join(x_ios_out_dir, "device"))
                run_shell(build_cmd, self.tool_dir)

                build_cmd = LibsBuilder.MAC_CMD_FMT % (proj_path, target, x_mac_out_dir)
                run_shell(build_cmd, self.tool_dir)

    def build_all_libs(self):
        # copy the necessary files
        self.copy_files()

        # build for iOS & Mac
        self.build_ios_mac()

if __name__ == "__main__":
    builder = LibsBuilder()
    builder.build_all_libs()
