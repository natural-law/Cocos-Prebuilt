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

ANDROID_SO_PATH = "frameworks/runtime-src/proj.android/libs"
ANDROID_A_PATH = "frameworks/runtime-src/proj.android/obj/local"
MK_PATH = "frameworks/runtime-src/proj.android/jni/Application.mk"
CONSOLE_PATH = "tools/cocos2d-console/bin"

MAKE_PKG_TOOL_PATH = "tools/make-package/git-archive-all"

def os_is_win32():
    return sys.platform == 'win32'

def os_is_mac():
    return sys.platform == 'darwin'

def run_shell(cmd, cwd=None):
    p = subprocess.Popen(cmd, shell=True, cwd=cwd)
    p.wait()

    if p.returncode:
        raise subprocess.CalledProcessError(returncode=p.returncode, cmd=cmd)

    return p.returncode

def unzip(source_filename, dest_dir):
    import zipfile
    z = zipfile.ZipFile(source_filename)
    for info in z.infolist():
        name = info.filename

        # don't extract absolute paths or ones with .. in them
        if name.startswith('/') or '..' in name:
            continue

        target = os.path.join(dest_dir, *name.split('/'))
        if not target:
            continue
        if name.endswith('/'):
            # directory
            if not os.path.exists(target):
                os.makedirs(target)
        else:
            # file
            data = z.read(info.filename)
            file_dir = os.path.dirname(target)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            f = open(target,'wb')
            try:
                f.write(data)
            finally:
                f.close()
                del data
        unix_attributes = info.external_attr >> 16
        if unix_attributes:
            os.chmod(target, unix_attributes)
    z.close()

class Generator(object):

    XCODE_CMD_FMT = "xcodebuild -project \"%s\" -configuration Release -target \"%s\" %s CONFIGURATION_BUILD_DIR=%s"

    # CONFIG_FILE = "gen_config.json"
    JS_CONFIG_FILE = "gen_config_js.json"
    X_CONFIG_FILE = "gen_config_x.json"
    KEY_COPY_CFG = "copy_config"
    KEY_ANDROID_MKS = "android_mks"
    KEY_XCODE_PROJ_INFO = "xcode_proj_info"
    KEY_WIN32_PROJ_INFO = "win32_proj_info"

    KEY_OUTPUT_DIR = "outputdir"
    KEY_TARGETS = "targets"

    def __init__(self, args):
        self.tool_dir = os.path.realpath(os.path.dirname(__file__))
        self.root_dir = os.path.join(self.tool_dir, os.path.pardir)
        self.need_clean = args.need_clean
        self.no_android = args.no_android
        self.use_incredibuild = args.use_incredibuild
        self.disable_strip = args.disable_strip

        self.x_repo_path = args.x_repo_path
        self.js_repo_path = args.js_repo_path
        self.gen_x = args.gen_x
        self.gen_js = args.gen_js

        if self.gen_x:
            if self.x_repo_path is not None:
                self.gen_engine_from_repo(self.x_repo_path, "cocos2d-x")
            elif not os.path.exists(os.path.join(self.root_dir, "cocos2d-x")):
                raise Exception("cocos2d-x is not existed, please specify cocos2d-x repo path by \"-x\".")

        if self.gen_js:
            if self.js_repo_path is not None:
                self.gen_engine_from_repo(self.js_repo_path, "cocos2d-js")
            elif not os.path.exists(os.path.join(self.root_dir, "cocos2d-js")):
                raise Exception("cocos2d-js is not existed, please specify cocos2d-js repo path by \"-js\".")

        self.load_config()

    def load_config(self):
        self.copy_cfg = []
        self.android_mks = []
        self.xcode_proj_info = {}
        self.win32_proj_info = {}
        if self.gen_x:
            # load x config
            x_cfg_json = os.path.join(self.tool_dir, Generator.X_CONFIG_FILE)
            f = open(x_cfg_json)
            x_cfg_info = json.load(f)
            f.close()
            self.copy_cfg += x_cfg_info[Generator.KEY_COPY_CFG]
            self.android_mks += x_cfg_info[Generator.KEY_ANDROID_MKS]
            for key in x_cfg_info[Generator.KEY_XCODE_PROJ_INFO].keys():
                self.xcode_proj_info[key] = x_cfg_info[Generator.KEY_XCODE_PROJ_INFO][key]

            for key in x_cfg_info[Generator.KEY_WIN32_PROJ_INFO].keys():
                self.win32_proj_info[key] = x_cfg_info[Generator.KEY_WIN32_PROJ_INFO][key]

        if self.gen_js:
            # load js config
            js_cfg_json = os.path.join(self.tool_dir, Generator.JS_CONFIG_FILE)
            f = open(js_cfg_json)
            js_cfg_info = json.load(f)
            f.close()
            self.copy_cfg += js_cfg_info[Generator.KEY_COPY_CFG]
            self.android_mks += js_cfg_info[Generator.KEY_ANDROID_MKS]
            for key in js_cfg_info[Generator.KEY_XCODE_PROJ_INFO].keys():
                self.xcode_proj_info[key] = js_cfg_info[Generator.KEY_XCODE_PROJ_INFO][key]

            for key in js_cfg_info[Generator.KEY_WIN32_PROJ_INFO].keys():
                self.win32_proj_info[key] = js_cfg_info[Generator.KEY_WIN32_PROJ_INFO][key]

    def gen_engine_from_repo(self, repo_dir, repo_name):
        # get the make-package tool
        tool_path = os.path.join(repo_dir, MAKE_PKG_TOOL_PATH)
        if not os.path.isfile(tool_path):
            print("\tCan't find the make-package tool")
            return

        zip_path = os.path.join(self.root_dir, "%s.zip" % repo_name)
        if os.path.isfile(zip_path):
            os.remove(zip_path)

        # run the tool
        print("> Generating the zip file")
        tool_dir_name = os.path.dirname(tool_path)
        cmd = "\"%s\" \"%s\"" % (tool_path, zip_path)
        run_shell(cmd, tool_dir_name)
        print("> Generate succeed!")

        # unzip the file
        print("> Unzip the file")
        unzip(zip_path, self.root_dir)
        print("> Unzip succeed!")

        # remove the zip file
        print("> Remove the zip file")
        os.remove(zip_path)
        print("> Remove succeed!")

    def copy_files(self):
        for cfg in self.copy_cfg:
            excopy.copy_files_with_config(cfg, self.root_dir, self.root_dir)

    def modify_mk(self, mk_file):
        if os.path.isfile(mk_file):
            file_obj = open(mk_file, "a")
            file_obj.write("\nAPP_ABI :=armeabi armeabi-v7a\n")
            file_obj.close()

    def is_32bit_windows(self):
        arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
        archw = os.environ.has_key("PROCESSOR_ARCHITEW6432")
        return (arch == "x86" and not archw)

    def build_android(self, language):
        # build .so for android
        if language == "js":
            engine_name = "cocos2d-js"
            prebuilt_dir = os.path.join(self.root_dir, "gen", "cocos", "frameworks", engine_name, "frameworks", "js-bindings", "cocos2d-x", "prebuilt", "android")
        else:
            engine_name = "cocos2d-x"
            prebuilt_dir = os.path.join(self.root_dir, "gen", "cocos", "frameworks", engine_name, "prebuilt", "android")

        engine_dir = os.path.join(self.root_dir, engine_name)
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
        target_libs_dir = os.path.join(self.root_dir, "gen", "cocos", "frameworks", engine_name, "templates", "%s-template-runtime" % language, ANDROID_SO_PATH)
        if os.path.exists(target_libs_dir):
            shutil.rmtree(target_libs_dir)
        shutil.copytree(libs_dir, target_libs_dir)

        # copy .a to prebuilt dir
        obj_dir = os.path.join(proj_path, ANDROID_A_PATH)
        copy_cfg = {
            "from": obj_dir,
            "to": prebuilt_dir,
            "include": [
                "*.a$"
            ]
        }
        excopy.copy_files_with_config(copy_cfg, obj_dir, prebuilt_dir)

        if not self.disable_strip:
            # strip the android libs
            ndk_root = os.environ["NDK_ROOT"]
            if os_is_win32():
                if self.is_32bit_windows():
                    bit_str = ""
                else:
                    bit_str = "-x86_64"

                sys_folder_name = "windows%s" % bit_str
            elif os_is_mac():
                sys_folder_name = "darwin-x86_64"

            strip_cmd_path = os.path.join(ndk_root, "toolchains/arm-linux-androideabi-4.8/prebuilt/%s/arm-linux-androideabi/bin/strip" % sys_folder_name)
            if os.path.exists(strip_cmd_path):
                strip_cmd = "%s -S %s/armeabi*/*.a" % (strip_cmd_path, prebuilt_dir)
                run_shell(strip_cmd)

        # modify the mk files to prebuilt version
        import gen_prebuilt_mk
        for mk_file in self.android_mks:
            mk_file_path = os.path.join(self.root_dir, mk_file)
            tmp_obj = gen_prebuilt_mk.MKGenerator(mk_file_path, prebuilt_dir, mk_file_path)
            tmp_obj.do_generate()

        # remove the project
        shutil.rmtree(proj_path)

        # build so with anysdk for runtime template
        # self.build_so_for_anysdk(language)

    def build_so_for_anysdk(self, language):
        if language == "js":
            engine_name = "cocos2d-js"
            proj_name = "PrebuiltRuntimeJs"
            pkg_name = "org.cocos2dx.PrebuiltRuntimeJs"
        else:
            engine_name = "cocos2d-x"
            proj_name = "PrebuiltRuntimeLua"
            pkg_name = "org.cocos2dx.PrebuiltRuntimeLua"

        # copy to tmp dir
        import tempfile
        tmp_dir = os.path.join(tempfile.gettempdir(), engine_name)
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        shutil.copytree(os.path.join(self.root_dir, "gen", "cocos", "frameworks", engine_name), tmp_dir)

        print("temp dir is %s" % tmp_dir)

        console_dir = os.path.join(tmp_dir, CONSOLE_PATH)
        cmd_path = os.path.join(console_dir, "cocos")
        proj_path = os.path.join(tmp_dir, proj_name)
        if os.path.exists(proj_path):
            shutil.rmtree(proj_path)

        # create a runtime project
        create_cmd = "%s new -l %s -t runtime -p %s -d %s %s" % (cmd_path, language, pkg_name, tmp_dir, proj_name)
        run_shell(create_cmd)

        # Add multi ABI in Application.mk
        mk_file = os.path.join(proj_path, MK_PATH)
        self.modify_mk(mk_file)

        # build it with release mode to get the so file
        build_cmd = "%s compile -s %s -p android --ndk-mode release -j 4" % (cmd_path, proj_path)
        run_shell(build_cmd)

        # copy .so to the template dir
        libs_dir = os.path.join(proj_path, ANDROID_SO_PATH)
        target_libs_dir = os.path.join(self.root_dir, "gen", "cocos", "frameworks", engine_name, "templates", "%s-template-runtime" % language, ANDROID_SO_PATH)
        if os.path.exists(target_libs_dir):
            shutil.rmtree(target_libs_dir)
        shutil.copytree(libs_dir, target_libs_dir)

        # build it with debug mode to get the prebuilt apk
        build_cmd = "%s compile -s %s -p android --no-res -j 4" % (cmd_path, proj_path)
        run_shell(build_cmd)

        # copy the apk into template dir
        apk_dir = os.path.join(proj_path, "runtime", "android", "%s-debug.apk" % proj_name)
        target_apk_path = os.path.join(self.root_dir, "gen", "cocos", "frameworks", engine_name, "templates", "%s-template-runtime" % language, "runtime", "android", "%s.apk" % proj_name)
        if os.path.exists(target_apk_path):
            os.remove(target_apk_path)
        shutil.copy(apk_dir, os.path.dirname(target_apk_path))
        os.rename(os.path.join(os.path.dirname(target_apk_path), "%s-debug.apk" % proj_name), target_apk_path)

        # remove the temp dir
        shutil.rmtree(tmp_dir)

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
            raise Exception("Can't parse the sln file to find required VS version")

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
            raise Exception(message)

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
            raise Exception(message)

        for key in self.win32_proj_info.keys():
            output_dir = self.win32_proj_info[key][Generator.KEY_OUTPUT_DIR]
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

            win32_output_dir = os.path.join(self.root_dir, output_dir)
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

            for proj_name in self.win32_proj_info[key][Generator.KEY_TARGETS]:
                # build the projects
                self.build_win32_proj(cmd_path, proj_path, proj_name, "build")

                lib_file_path = os.path.join(build_folder_path, "%s.lib" % proj_name)
                if not os.path.exists(lib_file_path):
                    # if the lib is not generated, rebuild the project
                    self.build_win32_proj(cmd_path, proj_path, proj_name, "rebuild")

                if not os.path.exists(lib_file_path):
                    raise Exception("Library %s not generated as expected!" % lib_file_path)

            # copy the libs into prebuilt dir
            for file_name in os.listdir(build_folder_path):
                file_path = os.path.join(build_folder_path, file_name)
                shutil.copy(file_path, win32_output_dir)

        print("Win32 build succeeded.")

         # modify the VS project file of templates
        import modify_template
        if self.gen_x:
            x_path = os.path.join(self.root_dir, "gen/cocos/frameworks/cocos2d-x")
            modifier = modify_template.TemplateModifier(x_path)
            cpp_proj_path = os.path.join(x_path, "templates/cpp-template-default/proj.win32/HelloCpp.vcxproj")
            lua_proj_path = os.path.join(x_path, "templates/lua-template-runtime/frameworks/runtime-src/proj.win32/HelloLua.vcxproj")
            modifier.modify_vs_proj(cpp_proj_path, "cpp")
            modifier.modify_vs_proj(lua_proj_path, "lua")

        if self.gen_js:
            js_path = os.path.join(self.root_dir, "gen/cocos/frameworks/cocos2d-js")
            modifier = modify_template.TemplateModifier(js_path)
            js_proj_path = os.path.join(js_path, "templates/js-template-runtime/frameworks/runtime-src/proj.win32/HelloJavascript.vcxproj")
            modifier.modify_vs_proj(js_proj_path, "js")

    def build_ios_mac(self):
        for key in self.xcode_proj_info.keys():
            output_dir = self.xcode_proj_info[key][Generator.KEY_OUTPUT_DIR]
            proj_path = os.path.join(self.root_dir, key)
            ios_out_dir = os.path.join(self.root_dir, output_dir, "ios")
            mac_out_dir = os.path.join(self.root_dir, output_dir, "mac")

            ios_sim_libs_dir = os.path.join(ios_out_dir, "simulator")
            ios_dev_libs_dir = os.path.join(ios_out_dir, "device")
            for target in self.xcode_proj_info[key][Generator.KEY_TARGETS]:
                build_cmd = Generator.XCODE_CMD_FMT % (proj_path, "%s iOS" % target, "-sdk iphonesimulator", ios_sim_libs_dir)
                run_shell(build_cmd, self.tool_dir)

                build_cmd = Generator.XCODE_CMD_FMT % (proj_path, "%s iOS" % target, "-sdk iphoneos", ios_dev_libs_dir)
                run_shell(build_cmd, self.tool_dir)

                build_cmd = Generator.XCODE_CMD_FMT % (proj_path, "%s Mac" % target, "", mac_out_dir)
                run_shell(build_cmd, self.tool_dir)

            # generate fat libs for iOS
            for lib in os.listdir(ios_sim_libs_dir):
                sim_lib = os.path.join(ios_sim_libs_dir, lib)
                dev_lib = os.path.join(ios_dev_libs_dir, lib)
                output_lib = os.path.join(ios_out_dir, lib)
                lipo_cmd = "lipo -create -output \"%s\" \"%s\" \"%s\"" % (output_lib, sim_lib, dev_lib)

                run_shell(lipo_cmd)

            # remove the simulator & device libs in iOS
            shutil.rmtree(ios_sim_libs_dir)
            shutil.rmtree(ios_dev_libs_dir)

            if not self.disable_strip:
                # strip the libs
                ios_strip_cmd = "xcrun -sdk iphoneos strip -S %s/*.a" % ios_out_dir
                run_shell(ios_strip_cmd)
                mac_strip_cmd = "xcrun strip -S %s/*.a" % mac_out_dir
                run_shell(mac_strip_cmd)

        # modify the xcode project file of templates
        import modify_template
        if self.gen_x:
            x_path = os.path.join(self.root_dir, "gen/cocos/frameworks/cocos2d-x")
            modifier = modify_template.TemplateModifier(x_path)
            cpp_proj_path = os.path.join(x_path, "templates/cpp-template-default/proj.ios_mac/HelloCpp.xcodeproj/project.pbxproj")
            lua_proj_path = os.path.join(x_path, "templates/lua-template-runtime/frameworks/runtime-src/proj.ios_mac/HelloLua.xcodeproj/project.pbxproj")
            modifier.modify_xcode_proj(cpp_proj_path, "cpp")
            modifier.modify_xcode_proj(lua_proj_path, "lua")

        if self.gen_js:
            js_path = os.path.join(self.root_dir, "gen/cocos/frameworks/cocos2d-js")
            modifier = modify_template.TemplateModifier(js_path)
            js_proj_path = os.path.join(js_path, "templates/js-template-runtime/frameworks/runtime-src/proj.ios_mac/HelloJavascript.xcodeproj/project.pbxproj")
            modifier.modify_xcode_proj(js_proj_path, "js")

    def build_all_libs(self):
        if os_is_mac():
            # build for iOS & Mac
            self.build_ios_mac()

        if os_is_win32():
            # build for win32
            self.build_win32()

        if not self.no_android:
            if self.gen_x:
                self.build_android("lua")
            if self.gen_js:
                self.build_android("js")

    def clean_gen(self):
        gen_dir = os.path.join(self.root_dir, "gen", "cocos", "frameworks")
        if os.path.exists(gen_dir):
            shutil.rmtree(gen_dir)

    def do_generate(self):
        if self.need_clean:
            # clean the files generated before
            self.clean_gen()

            # copy the necessary files
            self.copy_files()

            if self.gen_x:
                # create win32 directory in -x engine
                x_win32_dir = os.path.join(self.root_dir, "gen/cocos/frameworks/cocos2d-x/prebuilt/win32")
                if not os.path.exists(x_win32_dir):
                    os.makedirs(x_win32_dir)

            if self.gen_js:
                # create win32 directory in -js engine
                js_win32_dir = os.path.join(self.root_dir, "gen/cocos/frameworks/cocos2d-js/frameworks/js-bindings/cocos2d-x/prebuilt/win32")
                if not os.path.exists(js_win32_dir):
                    os.makedirs(js_win32_dir)

        self.build_all_libs()

if __name__ == "__main__":
    parser = ArgumentParser(description="Generate prebuilt engine for Cocos Engine.")
    parser.add_argument('-c', dest='need_clean', action="store_true", help='Remove the \"gen/cocos/frameworks\" directory first, and copy files again.')
    parser.add_argument('-n', "--no-android", dest='no_android', action="store_true", help='Not build android so.')
    parser.add_argument('-i', "--incredibuild", dest='use_incredibuild', action="store_true", help='Use incredibuild to build win32 projects. Only available on windows.')
    parser.add_argument('-x', "--cocos2dx", dest='x_repo_path', help='Set the repo path of cocos2d-x.')
    parser.add_argument('-j', "--cocos2djs", dest='js_repo_path', help='Set the repo path of cocos2d-js.')
    parser.add_argument('-d', "--disable-strip", dest='disable_strip', action="store_true", help='Disable the strip of the generated libs.')
    parser.add_argument('--gen-x', dest='gen_x', action="store_true", help='Generate cocos2d-x engine.')
    parser.add_argument('--gen-js', dest='gen_js', action="store_true", help='Generate cocos2d-js engine.')
    (args, unknown) = parser.parse_known_args()

    if len(unknown) > 0:
        print("unknown arguments: %s" % unknown)

    gen_obj = Generator(args)
    gen_obj.do_generate()
