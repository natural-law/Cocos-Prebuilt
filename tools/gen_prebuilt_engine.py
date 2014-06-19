#!/usr/bin/python
# ----------------------------------------------------------------------------
# generate the prebuilt engine for Cocos Engine
#
# Copyright 2014 (C) zhangbin
#
# License: MIT
# ----------------------------------------------------------------------------
'''
Generate the prebuilt engine for Cocos Engine
'''

import os
import subprocess
import shutil
import sys
import excopy
import json

XCODE_PROJ_INFO = {
    "cocos2d-x/build/cocos2d_libs.xcodeproj" : [ "build all libs" ],
    "cocos2d-x/cocos/scripting/lua-bindings/proj.ios_mac/cocos2d_lua_bindings.xcodeproj" : [ "luabindings" ]
}

X_IOS_OUTPUT_DIR = "gen/cocos2d-x/prebuilt/ios"
X_MAC_OUTPUT_DIR = "gen/cocos2d-x/prebuilt/mac"

LIBS_PATH = "frameworks/runtime-src/proj.android/libs"
MK_PATH = "frameworks/runtime-src/proj.android/jni/Application.mk"
CONSOLE_PATH = "tools/cocos2d-console/bin"

def os_is_win32():
    return sys.platform == 'win32'

def os_is_mac():
    return sys.platform == 'darwin'

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

class Generator(object):

    XCODE_CMD_FMT = "xcodebuild -project \"%s\" -configuration Release -target \"%s\" %s CONFIGURATION_BUILD_DIR=%s"
    COPY_CFG_FILE = "copy_config.json"

    def __init__(self):
        self.tool_dir = os.path.realpath(os.path.dirname(__file__))
        self.root_dir = os.path.join(self.tool_dir, os.path.pardir)
        self.copy_cfg = self.load_copy_cfg()

    def load_copy_cfg(self):
        cfg_json = os.path.join(self.tool_dir, Generator.COPY_CFG_FILE)
        f = open(cfg_json)
        cfg_info = json.load(f)
        f.close()

        return cfg_info

    def copy_files(self):
        for cfg in self.copy_cfg:
            excopy.copy_files_with_config(cfg, self.root_dir, self.root_dir)

    def modify_mk(self, mk_file):
        if os.path.isfile(mk_file):
            file_obj = open(mk_file, "a")
            file_obj.write("\nAPP_ABI :=armeabi armeabi-v7a x86\n")
            file_obj.close()

    def build_android(self, language):
        # build .so for android
        if language == "js":
            engine_dir = os.path.join(self.root_dir, "cocos2d-js")
        else:
            engine_dir = os.path.join(self.root_dir, "cocos2d-x")

        console_dir = os.path.join(engine_dir, CONSOLE_PATH)
        cmd_path = os.path.join(console_dir, "cocos")
        proj_name = "My%sGame" % language
        proj_path = os.path.join(engine_dir, proj_name)
        if os.path.exists(proj_path):
            shutil.rmtree(proj_path)

        # create a runtime project
        create_cmd = "%s new -l %s -t runtime -d %s %s" % (cmd_path, language, engine_dir, proj_name)
        run_shell(create_cmd)

        # Add multi ABI in Application.mk
        mk_file = os.path.join(proj_path, MK_PATH)
        self.modify_mk(mk_file)

        # build it
        build_cmd = "%s compile -s %s -p android --ndk-mode release -j 4" % (cmd_path, proj_path)
        run_shell(build_cmd)

        # copy libs to the template dir
        libs_dir = os.path.join(proj_path, LIBS_PATH)
        target_libs_dir = os.path.join(self.root_dir, "gen", os.path.basename(engine_dir), "templates", "%s-template-runtime" % language, LIBS_PATH)
        shutil.copytree(libs_dir, target_libs_dir)

        # remove the project
        shutil.rmtree(proj_path)

    def build_win32(self):
        print("build win32 invoked!")

    def build_ios_mac(self):
        x_ios_out_dir = os.path.join(self.root_dir, X_IOS_OUTPUT_DIR)
        x_mac_out_dir = os.path.join(self.root_dir, X_MAC_OUTPUT_DIR)
        x_ios_sim_libs_dir = os.path.join(x_ios_out_dir, "simulator")
        x_ios_dev_libs_dir = os.path.join(x_ios_out_dir, "device")
        for key in XCODE_PROJ_INFO.keys():
            proj_path = os.path.join(self.root_dir, key)
            for target in XCODE_PROJ_INFO[key]:
                build_cmd = Generator.XCODE_CMD_FMT % (proj_path, "%s iOS" % target, "-sdk iphonesimulator", x_ios_sim_libs_dir)
                run_shell(build_cmd, self.tool_dir)

                build_cmd = Generator.XCODE_CMD_FMT % (proj_path, "%s iOS" % target, "-sdk iphoneos", x_ios_dev_libs_dir)
                run_shell(build_cmd, self.tool_dir)

                build_cmd = Generator.XCODE_CMD_FMT % (proj_path, "%s Mac" % target, "", x_mac_out_dir)
                run_shell(build_cmd, self.tool_dir)

        # generate fat libs for iOS
        for lib in os.listdir(x_ios_sim_libs_dir):
            sim_lib = os.path.join(x_ios_sim_libs_dir, lib)
            dev_lib = os.path.join(x_ios_dev_libs_dir, lib)
            output_lib = os.path.join(x_ios_out_dir, lib)
            lipo_cmd = "lipo -create -output \"%s\" \"%s\" \"%s\"" % (output_lib, sim_lib, dev_lib)

            run_shell(lipo_cmd)

        # remove the simulator & device libs in iOS
        shutil.rmtree(x_ios_sim_libs_dir)
        shutil.rmtree(x_ios_dev_libs_dir)

    def build_all_libs(self):
        if os_is_mac():
            # build for iOS & Mac
            self.build_ios_mac()

        if os_is_win32():
            # build for win32
            self.build_win32()

        self.build_android("lua")

    def clean_gen(self):
        gen_dir = os.path.join(self.root_dir, "gen")
        if os.path.exists(gen_dir):
            shutil.rmtree(gen_dir)

    def do_generate(self):
        # clean the files generated before
        self.clean_gen()

        # copy the necessary files
        self.copy_files()

        self.build_all_libs()

if __name__ == "__main__":
    gen_obj = Generator()
    gen_obj.do_generate()
