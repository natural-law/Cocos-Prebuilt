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

from argparse import ArgumentParser

if sys.platform == 'win32':
    import _winreg

XCODE_PROJ_INFO = {
    "cocos2d-x/build/cocos2d_libs.xcodeproj" : [ "build all libs" ],
    "cocos2d-x/cocos/scripting/lua-bindings/proj.ios_mac/cocos2d_lua_bindings.xcodeproj" : [ "luabindings" ]
}

X_IOS_OUTPUT_DIR = "gen/cocos2d-x/prebuilt/ios"
X_MAC_OUTPUT_DIR = "gen/cocos2d-x/prebuilt/mac"
X_WIN32_OUTPUT_DIR = "gen/cocos2d-x/prebuilt/win32"
X_ANDROID_OUTPUT_DIR = "gen/cocos2d-x/prebuilt/android"

ANDROID_SO_PATH = "frameworks/runtime-src/proj.android/libs"
ANDROID_A_PATH = "frameworks/runtime-src/proj.android/obj/local"
MK_PATH = "frameworks/runtime-src/proj.android/jni/Application.mk"
CONSOLE_PATH = "tools/cocos2d-console/bin"

WIN32_PROJ_INFO = {
    "cocos2d-x/build/cocos2d-win32.vc2012.sln" : [
        "libAudio", "libBox2D", "libchipmunk",
        "libcocos2d", "libCocosBuilder", "libCocosStudio",
        "libExtensions", "libGUI", "libLocalStorage",
        "liblua", "libNetwork", "libSpine"
    ]
}

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

class GenerateError(Exception):
    pass

class Generator(object):

    XCODE_CMD_FMT = "xcodebuild -project \"%s\" -configuration Release -target \"%s\" %s CONFIGURATION_BUILD_DIR=%s"
    COPY_CFG_FILE = "copy_config.json"
    ANDROID_LIBS_CFG = "android_mks.json"

    def __init__(self, args):
        self.tool_dir = os.path.realpath(os.path.dirname(__file__))
        self.root_dir = os.path.join(self.tool_dir, os.path.pardir)
        self.copy_cfg = self.load_copy_cfg()
        self.need_clean = args.need_clean
        self.no_android = args.no_android
        self.use_incredibuild = args.use_incredibuild

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
            file_obj.write("\nAPP_ABI :=armeabi armeabi-v7a\n")
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

        # copy .so to the template dir
        libs_dir = os.path.join(proj_path, ANDROID_SO_PATH)
        target_libs_dir = os.path.join(self.root_dir, "gen", os.path.basename(engine_dir), "templates", "%s-template-runtime" % language, ANDROID_SO_PATH)
        if os.path.exists(target_libs_dir):
            shutil.rmtree(target_libs_dir)
        shutil.copytree(libs_dir, target_libs_dir)

        # copy .a to prebuilt dir
        obj_dir = os.path.join(proj_path, ANDROID_A_PATH)
        prebuilt_dir = os.path.join(self.root_dir, X_ANDROID_OUTPUT_DIR)
        copy_cfg = {
            "from": obj_dir,
            "to": prebuilt_dir,
            "include": [
                "*.a$"
            ]
        }
        excopy.copy_files_with_config(copy_cfg, obj_dir, prebuilt_dir)

        # modify the mk files to prebuilt version
        android_mks_json = os.path.join(self.tool_dir, Generator.ANDROID_LIBS_CFG)
        f = open(android_mks_json)
        mk_files = json.load(f)
        f.close()
        import gen_prebuilt_mk
        for mk_file in mk_files:
            mk_file_path = os.path.join(self.root_dir, "gen", "cocos2d-x", mk_file)
            tmp_obj = gen_prebuilt_mk.MKGenerator(mk_file_path, prebuilt_dir, mk_file_path)
            tmp_obj.do_generate()

        # remove the project
        shutil.rmtree(proj_path)

    def get_required_vs_version(self, proj_file):
        # get the VS version required by the project
        import re
        file_obj = open(proj_file)
        pattern = re.compile(r"^# Visual Studio.+(\d{4})")
        num = None
        for line in file_obj:
            match = pattern.match(line)
            if match is not None:
                num = match.group(1)
                break

        if num is not None:
            if num == "2012":
                ret = "11.0"
            elif num == "2013":
                ret = "12.0"
            else:
                ret = None
        else:
            ret = None

        return ret

    def get_vs_cmd_path(self, vs_reg, proj_path):
        # get required vs version
        required_vs_version = self.get_required_vs_version(proj_path)
        if required_vs_version is None:
            raise GenerateError("Can't parse the sln file to find required VS version")

        # get the correct available VS path
        needUpgrade = False
        vsPath = None
        i = 0
        try:
            while True:
                version = _winreg.EnumKey(vs_reg, i)
                try:
                    if float(version) >= float(required_vs_version):
                        key = _winreg.OpenKey(vs_reg, r"SxS\VS7")
                        vsPath, type = _winreg.QueryValueEx(key, version)

                        if float(version) > float(required_vs_version):
                            needUpgrade = True

                        key.close()
                        break
                except:
                    pass
                i += 1
        except WindowsError:
            pass

        if vsPath is None:
            message = "Can't find correct Visual Studio's path in the regedit"
            raise GenerateError(message)

        commandPath = os.path.join(vsPath, "Common7", "IDE", "devenv")
        return (commandPath, needUpgrade)

    def _is_32bit_windows(self):
        arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
        archw = os.environ.has_key("PROCESSOR_ARCHITEW6432")
        return (arch == "x86" and not archw)

    def build_win32_proj(self, cmd_path, sln_path, proj_name, mode):
        if self.use_incredibuild:
            build_cmd = " ".join([
                "\"%s\"" % cmd_path,
                "\"%s\"" % sln_path,
                "/%s" % mode,
                "/prj=%s" % proj_name,
                "/cfg=\"Release|Win32\""
            ])
        else:
            build_cmd = " ".join([
                "\"%s\"" % cmd_path,
                "\"%s\"" % sln_path,
                "/%s \"Release|Win32\"" % mode,
                "/Project \"%s\"" % proj_name
            ])
        run_shell(build_cmd)

    def build_win32(self):
        print("Building Win32")

        # find the VS in register
        try:
            if self._is_32bit_windows():
                reg_flag = _winreg.KEY_WOW64_32KEY
            else:
                reg_flag = _winreg.KEY_WOW64_64KEY

            vs_reg = _winreg.OpenKey(
                _winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\VisualStudio",
                0,
                _winreg.KEY_READ | reg_flag
            )

        except WindowsError:
            message = "Visual Studio wasn't installed"
            raise GenerateError(message)

        for key in WIN32_PROJ_INFO.keys():
            proj_path = os.path.join(self.root_dir, key)
            vs_command, needUpgrade = self.get_vs_cmd_path(vs_reg, proj_path)

            if self.use_incredibuild:
                cmd_path = "BuildConsole"
            else:
                cmd_path = vs_command

            # get the build folder & win32 output folder
            build_folder_path = os.path.join(os.path.dirname(proj_path), "Release.win32")
            if os.path.exists(build_folder_path):
                shutil.rmtree(build_folder_path)
            os.makedirs(build_folder_path)

            win32_output_dir = os.path.join(self.root_dir, X_WIN32_OUTPUT_DIR)
            if os.path.exists(win32_output_dir):
                shutil.rmtree(win32_output_dir)
            os.makedirs(win32_output_dir)

            # upgrade projects
            if needUpgrade:
                commandUpgrade = ' '.join([
                    "\"%s\"" % vs_command,
                    "\"%s\"" % proj_path,
                    "/Upgrade"
                ])
                run_shell(commandUpgrade)

            for proj_name in WIN32_PROJ_INFO[key]:
                # build the projects
                self.build_win32_proj(cmd_path, proj_path, proj_name, "build")

                lib_file_path = os.path.join(build_folder_path, "%s.lib" % proj_name)
                if not os.path.exists(lib_file_path):
                    # if the lib is not generated, rebuild the project
                    self.build_win32_proj(cmd_path, proj_path, proj_name, "rebuild")

                if not os.path.exists(lib_file_path):
                    raise GenerateError("Library %s not generated as expected!" % lib_file_path)

            # copy the libs into prebuilt dir
            for file_name in os.listdir(build_folder_path):
                file_path = os.path.join(build_folder_path, file_name)
                shutil.copy(file_path, win32_output_dir)

        print("Win32 build succeeded.")

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

        if not self.no_android:
            self.build_android("lua")

    def clean_gen(self):
        gen_dir = os.path.join(self.root_dir, "gen")
        if os.path.exists(gen_dir):
            shutil.rmtree(gen_dir)

    def do_generate(self):
        if self.need_clean:
            # clean the files generated before
            self.clean_gen()

            # copy the necessary files
            self.copy_files()

        self.build_all_libs()

if __name__ == "__main__":
    parser = ArgumentParser(description="Generate prebuilt engine for Cocos Engine.")
    parser.add_argument('-c', dest='need_clean', action="store_true", help='Remove the \"gen\" directory first, and copy files again.')
    parser.add_argument('-n', "--no-android", dest='no_android', action="store_true", help='Not build android so.')
    parser.add_argument('-i', "--incredibuild", dest='use_incredibuild', action="store_true", help='Use incredibuild to build win32 projects. Only available on windows.')
    (args, unknown) = parser.parse_known_args()

    if len(unknown) > 0:
        print("unknown arguments: %s" % unknown)

    gen_obj = Generator(args)
    gen_obj.do_generate()
