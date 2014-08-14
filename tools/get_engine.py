#!/usr/bin/python
# ----------------------------------------------------------------------------
# get the prebuilt engine for Cocos Engine
#
# Copyright 2014 (C) zhangbin
#
# License: MIT
# ----------------------------------------------------------------------------
'''
Get the prebuilt engine for Cocos Engine
'''

import os
import subprocess
import shutil
import excopy
import json

from argparse import ArgumentParser

def run_shell(cmd, cwd=None):
    p = subprocess.Popen(cmd, shell=True, cwd=cwd)
    p.wait()

    if p.returncode:
        raise subprocess.CalledProcessError(returncode=p.returncode, cmd=cmd)

    return p.returncode

DST_PATH = "gen/cocos/frameworks"

MODULE_TOOL_PATH = "tools/gen-prebuilt/module_organize.py"

COPY_CONFIG_FILE = "copy_config.json"
KEY_COPY_ENGINE = "copy-engine"
KEY_COPY_MODIFIED = "copy-modified"

CONSOLE_PATH = "tools/cocos2d-console/bin"
ANDROID_SO_PATH = "frameworks/runtime-src/proj.android/libs"

class GetEngine(object):

    def __init__(self, args):
        self.tool_dir = os.path.realpath(os.path.dirname(__file__))
        self.root_dir = os.path.join(self.tool_dir, os.path.pardir)
        self.dst_dir  = os.path.join(self.root_dir, DST_PATH)

        self.x_engine_path = None
        if args.x_engine_path is not None:
            if os.path.isabs(args.x_engine_path):
                self.x_engine_path = args.x_engine_path
            else:
                self.x_engine_path = os.path.abspath(args.x_engine_path)

        self.js_engine_path = None
        if args.js_engine_path is not None:
            if os.path.isabs(args.js_engine_path):
                self.js_engine_path = args.js_engine_path
            else:
                self.js_engine_path = os.path.abspath(args.js_engine_path)

    def generate_so(self, engine_name):
        engine_dst_path = os.path.join(self.dst_dir, engine_name)
        if engine_name == "cocos2d-x":
            language = "lua"
            proj_name = "PrebuiltRuntimeLua"
            pkg_name = "org.cocos2dx.PrebuiltRuntimeLua"
        else:
            language = "js"
            proj_name = "PrebuiltRuntimeJs"
            pkg_name = "org.cocos2dx.PrebuiltRuntimeJs"

        # copy the engine to temp dir
        import tempfile
        temp_dir = os.path.join(tempfile.gettempdir(), engine_name)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        shutil.copytree(engine_dst_path, temp_dir)

        print("temp dir is %s" % temp_dir)

        console_dir = os.path.join(temp_dir, CONSOLE_PATH)
        cmd_path = os.path.join(console_dir, "cocos")
        proj_path = os.path.join(temp_dir, proj_name)
        if os.path.exists(proj_path):
            shutil.rmtree(proj_path)

        # create a runtime project
        create_cmd = "%s new -l %s -t runtime -p %s -d %s %s" % (cmd_path, language, pkg_name, temp_dir, proj_name)
        run_shell(create_cmd)

        # build it with release mode to get the so file
        build_cmd = "%s compile -s %s -p android --ndk-mode release -j 4" % (cmd_path, proj_path)
        run_shell(build_cmd)

        # copy .so to the template dir
        libs_dir = os.path.join(proj_path, ANDROID_SO_PATH)
        target_libs_dir = os.path.join(engine_dst_path, "templates", "%s-template-runtime" % language, ANDROID_SO_PATH)
        if os.path.exists(target_libs_dir):
            shutil.rmtree(target_libs_dir)
        shutil.copytree(libs_dir, target_libs_dir)

        # remove the temp dir
        shutil.rmtree(temp_dir)

    def generate_engine(self, engine_path, dst_engine_name):
        engine_dst_path = os.path.join(self.dst_dir, dst_engine_name)
        if os.path.exists(engine_dst_path):
            shutil.rmtree(engine_dst_path)

        # get the prebuilt modules
        module_cmd_path = os.path.join(engine_path, MODULE_TOOL_PATH)
        dst_dir = os.path.join(self.root_dir, DST_PATH)
        module_cmd = "python %s -d %s" % (module_cmd_path, dst_dir)

        run_shell(module_cmd)

        copy_cfg_file = os.path.join(self.tool_dir, COPY_CONFIG_FILE)
        f = open(copy_cfg_file)
        copy_cfg = json.load(f)
        f.close()

        # copy files from engine
        for item in copy_cfg[dst_engine_name][KEY_COPY_ENGINE]:
            excopy.copy_files_with_config(item, engine_path, engine_dst_path)

        # copy files from current root dir
        for item in copy_cfg[dst_engine_name][KEY_COPY_MODIFIED]:
            excopy.copy_files_with_config(item, self.root_dir, engine_dst_path)

        # modify the runtime templates
        if dst_engine_name == "cocos2d-x":
            import modify_lua_template
            modifier = modify_lua_template.LuaModifier(engine_dst_path)
            modifier.do_modify()
        
        # generate android so
        self.generate_so(dst_engine_name)

    def do_generate(self):
        if self.x_engine_path is not None:
            self.generate_engine(self.x_engine_path, "cocos2d-x")

        if self.js_engine_path is not None:
            self.generate_engine(self.js_engine_path, "cocos2d-js")

if __name__ == "__main__":
    parser = ArgumentParser(description="Generate prebuilt engine for Cocos Engine.")
    parser.add_argument('-x', "--cocos2dx", dest='x_engine_path', help='Set the path of cocos2d-x.')
    parser.add_argument('-j', "--cocos2djs", dest='js_engine_path', help='Set the path of cocos2d-js.')
    (args, unknown) = parser.parse_known_args()

    if len(unknown) > 0:
        print("unknown arguments: %s" % unknown)

    get_obj = GetEngine(args)
    get_obj.do_generate()
