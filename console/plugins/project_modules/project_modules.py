#!/usr/bin/python
# ----------------------------------------------------------------------------
# cocos2d "modules" plugin
#
# Copyright 2014 (C) Bill Zhang. Chukong-inc.com
#
# License: MIT
# ----------------------------------------------------------------------------
'''
"modules" plugin for cocos command line tool
'''

__docformat__ = 'restructuredtext'

import cocos
import cocos_project
import os
import json

import modify_pbxproj
import modify_mk
import modify_vcxproj

class CCPluginModules(cocos.CCPlugin):
    """
    compiles a project
    """

    CONSTANT_MODULES = [
        "cocos2d"
    ]

    PROJ_CFG_KEY_MODULES = "modules"

    MODULE_INFO_FILE = "modules-info.json"
    X_ENGINE_PATH = "frameworks/cocos2d-x"
    JS_ENGINE_PATH = "frameworks/js-bindings"

    KEY_MODULE_WIN32_LIB_FILE_NAME = "win32_lib_file_name"
    KEY_MODULE_IOS_LIB_FILE_NAME = "ios_lib_file_name"
    KEY_MODULE_MAC_LIB_FILE_NAME = "mac_lib_file_name"
    KEY_MODULE_TARGET_DIR = "target_dir"
    KEY_MODULE_ANDROID_LIB_NAME = "android_lib_name"
    KEY_MODULE_LUA_BINDINGS = "lua_bindings"
    KEY_MODULE_JS_BINDINGS = "js_bindings"
    KEY_MODULE_IS_OPTIONAL = "is_optional"
    KEY_MODULE_IS_COMPILED = "is_compiled"
    KEY_MODULE_LUA_LIB_NAME = "lua_lib_name"
    KEY_MODULE_JS_LIB_NAME = "js_lib_name"
    KEY_MODULE_DEPEND_MODULES = "depend_modules"
    KEY_MODULE_ADDITIONAL_LINK = "additional_link"
    KEY_MODULE_BINDING_HEADERS = "headers"
    KEY_MODULE_BINDING_REGISTERS = "registers"

    KEY_DELTA_IOS_LIBS = "ios_libs"
    KEY_DELTA_MAC_LIBS = "mac_libs"
    KEY_DELTA_ANDROID_LIBS = "android_libs"
    KEY_DELTA_WIN32_LIBS = "win32_libs"
    KEY_DELTA_LUA_PATHS = "lua_paths"
    KEY_DELTA_JS_PATHS = "js_paths"

    CHECK_PLATFORMS = [
        cocos_project.Platforms.IOS,
        cocos_project.Platforms.MAC,
        cocos_project.Platforms.ANDROID,
        cocos_project.Platforms.WIN32,
    ]

    KEY_CFG_LIB_NAME = "lib_name"
    KEY_CFG_LIB_EXT  = "lib_ext"
    KEY_CFG_LIB_DELTA_KAY = "delta_key"
    PLATFORM_CONFIG = {
        cocos_project.Platforms.IOS : {
            KEY_CFG_LIB_NAME: KEY_MODULE_IOS_LIB_FILE_NAME,
            KEY_CFG_LIB_EXT: ".a",
            KEY_CFG_LIB_DELTA_KAY: KEY_DELTA_IOS_LIBS
        },
        cocos_project.Platforms.MAC : {
            KEY_CFG_LIB_NAME: KEY_MODULE_MAC_LIB_FILE_NAME,
            KEY_CFG_LIB_EXT: ".a",
            KEY_CFG_LIB_DELTA_KAY: KEY_DELTA_MAC_LIBS
        },
        cocos_project.Platforms.ANDROID : {
            KEY_CFG_LIB_NAME: KEY_MODULE_ANDROID_LIB_NAME,
            KEY_CFG_LIB_EXT: ".a",
            KEY_CFG_LIB_DELTA_KAY: KEY_DELTA_ANDROID_LIBS
        },
        cocos_project.Platforms.WIN32 : {
            KEY_CFG_LIB_NAME: KEY_MODULE_WIN32_LIB_FILE_NAME,
            KEY_CFG_LIB_EXT: ".lib",
            KEY_CFG_LIB_DELTA_KAY: KEY_DELTA_WIN32_LIBS
        }
    }

    XCODE_LUA_GROUP = "Lua Common"
    XCODE_JS_GROUP = "JS Common"

    BUILD_CFG_FILE_NAME = "build-cfg.json"

    @staticmethod
    def plugin_name():
      return "modules"

    @staticmethod
    def brief_description():
        return "Customize the modules of cocos project."

    def parse_args(self, argv):
        from argparse import ArgumentParser
        parser = ArgumentParser(prog="cocos %s" % self.__class__.plugin_name(),
                                description=self.__class__.brief_description())

        parser.add_argument("-s", "--src",
                          dest="src_dir",
                          help="Project base directory")

        parser.add_argument("-m", "--modules", dest="select_modules",
                            help="Specify the selected modules. If select multi-modules, split with ':'.")

        (args, unkonw) = parser.parse_known_args(argv)

        # generate project object
        if args.src_dir is None:
            self._project = cocos_project.Project(os.path.abspath(os.getcwd()))
        else:
            self._project = cocos_project.Project(os.path.abspath(args.src_dir))

        # generate supported platforms
        self.available_platforms = self.gen_available_platforms()

        # get the engine dir of project
        if self._project._is_js_project():
            self.engine_dir = os.path.join(self._project.get_project_dir(), CCPluginModules.JS_ENGINE_PATH)
        else:
            self.engine_dir = os.path.join(self._project.get_project_dir(), CCPluginModules.X_ENGINE_PATH)

        # get selected modules from args
        if args.select_modules is None:
            self.select_modules = []
        else:
            self.select_modules = args.select_modules.split(":")

        # get current modules
        self.cur_modules = self._project.get_proj_config(CCPluginModules.PROJ_CFG_KEY_MODULES)
        if self.cur_modules is None:
            self.cur_modules = []

        # get modules info of engine
        info_file = os.path.join(self.engine_dir, CCPluginModules.MODULE_INFO_FILE)
        f = open(info_file)
        self.modules_info = json.load(f)
        f.close()

    def gen_available_platforms(self):
        root_path = self._project.get_project_dir()
        proj_info = self._project.info
        ret = {}
        for p in CCPluginModules.CHECK_PLATFORMS:
            cfg_class = cocos.get_class(cocos_project.Platforms.CFG_CLASS_MAP[p])
            if cfg_class is None:
                continue

            cfg_key = "%s_cfg" % p
            if proj_info.has_key(cfg_key):
                cfg_obj = cfg_class(root_path, self._project._is_script_project(), proj_info[cfg_key])
            else:
                cfg_obj = cfg_class(root_path, self._project._is_script_project())

            if cfg_obj._is_available():
                ret[p] = cfg_obj

        return ret

    def get_module_info(self, module_name):
        ret = None
        if self.modules_info.has_key(module_name):
            ret = self.modules_info[module_name]

        return ret

    def checkFileByExtention(self, ext, path):
        filelist = os.listdir(path)
        for fullname in filelist:
            name, extention = os.path.splitext(fullname)
            if extention == ext:
                return name, fullname
        return (None, None)

    def get_xcode_proj_info(self, platform):
        proj_cfg = self.available_platforms[platform]
        proj_path = proj_cfg.proj_path
        if proj_cfg.proj_file is not None:
            proj_file = proj_cfg.proj_file
            proj_name = os.path.basename(proj_file)
        else:
            proj_name, proj_file = self.checkFileByExtention(".xcodeproj", proj_path)

        proj_file = os.path.join(proj_path, proj_file, "project.pbxproj")
        return (proj_name, proj_file)

    def get_platform_cfg(self, platform, cfg_key):
        return CCPluginModules.PLATFORM_CONFIG[platform][cfg_key]

    def init_delta_info(self):
        ret = {
            CCPluginModules.KEY_DELTA_IOS_LIBS: {},
            CCPluginModules.KEY_DELTA_MAC_LIBS: {},
            CCPluginModules.KEY_DELTA_ANDROID_LIBS: {},
            CCPluginModules.KEY_DELTA_WIN32_LIBS: {},
            CCPluginModules.KEY_DELTA_LUA_PATHS: [],
            CCPluginModules.KEY_DELTA_JS_PATHS: []
        }
        return ret

    def is_support_platform(self, platform, module_name):
        ret = False
        if not self.available_platforms.has_key(platform):
            cocos.Logging.warning("The project is not support %s platform." % platform)
            return ret

        module_info = self.get_module_info(module_name)
        key = self.get_platform_cfg(platform, CCPluginModules.KEY_CFG_LIB_NAME)
        if module_info.has_key(key):
            ret = True
        else:
            cocos.Logging.warning("Module %s is not support %s platform." % (module_name, platform))

        return ret

    def get_android_delta_info(self, module_info):
        if self._project._is_js_project() and module_info.has_key(CCPluginModules.KEY_MODULE_JS_BINDINGS):
            android_lib = module_info[CCPluginModules.KEY_MODULE_JS_BINDINGS][CCPluginModules.KEY_MODULE_ANDROID_LIB_NAME]
            android_lib_path = os.path.join(module_info[CCPluginModules.KEY_MODULE_TARGET_DIR], "js-bindings", "prebuilt", "android")
        elif self._project._is_lua_project() and module_info.has_key(CCPluginModules.KEY_MODULE_LUA_BINDINGS):
            android_lib = module_info[CCPluginModules.KEY_MODULE_LUA_BINDINGS][CCPluginModules.KEY_MODULE_ANDROID_LIB_NAME]
            android_lib_path = os.path.join(module_info[CCPluginModules.KEY_MODULE_TARGET_DIR], "lua-bindings", "prebuilt", "android")
        else:
            android_lib = module_info[CCPluginModules.KEY_MODULE_ANDROID_LIB_NAME]
            android_lib_path = os.path.join(module_info[CCPluginModules.KEY_MODULE_TARGET_DIR], "prebuilt", "android")

        return (android_lib, android_lib_path)

    def gather_additional_link(self, platform, module_info, libs_info):
        if not module_info.has_key(CCPluginModules.KEY_MODULE_ADDITIONAL_LINK):
            return libs_info

        add_link_info = module_info[CCPluginModules.KEY_MODULE_ADDITIONAL_LINK]
        if not add_link_info.has_key(platform):
            return libs_info

        for key in add_link_info[platform].keys():
            libs_info[key] = add_link_info[platform][key]

        return libs_info

    def get_delta_info(self, module_name, platform, libs_info=None):
        if libs_info is None:
            libs_info = {}

        if module_name in CCPluginModules.CONSTANT_MODULES:
            return libs_info

        module_info = self.get_module_info(module_name)
        # add the additional libs
        libs_info = self.gather_additional_link(platform, module_info, libs_info)

        # add the depend modules info
        if module_info.has_key(CCPluginModules.KEY_MODULE_DEPEND_MODULES):
            for d in module_info[CCPluginModules.KEY_MODULE_DEPEND_MODULES]:
                libs_info = self.get_delta_info(d, platform, libs_info=libs_info)

        if platform in (cocos_project.Platforms.IOS, cocos_project.Platforms.MAC) and not module_info[CCPluginModules.KEY_MODULE_IS_COMPILED]:
            return libs_info

        platform_surfix = {
            cocos_project.Platforms.IOS : " iOS",
            cocos_project.Platforms.MAC : " Mac",
            cocos_project.Platforms.WIN32 : ""
        }

        proj_cfg = self.available_platforms[platform]
        proj_path = proj_cfg.proj_path
        module_dir = module_info[CCPluginModules.KEY_MODULE_TARGET_DIR]
        lib_path = os.path.join(self.engine_dir, module_dir, "prebuilt", platform)
        lib_path = os.path.relpath(lib_path, proj_path)

        lib = module_info[self.get_platform_cfg(platform, CCPluginModules.KEY_CFG_LIB_NAME)]
        libs_info[lib] = lib_path

        # add lib & lib_path of script bindings
        if self._project._is_js_project() and module_info.has_key(CCPluginModules.KEY_MODULE_JS_BINDINGS):
            lib_name = module_info[CCPluginModules.KEY_MODULE_JS_BINDINGS][CCPluginModules.KEY_MODULE_JS_LIB_NAME]
            lib_binding = "%s%s%s" % (lib_name, platform_surfix[platform], self.get_platform_cfg(platform, CCPluginModules.KEY_CFG_LIB_EXT))
            lib_binding_path = os.path.join(self.engine_dir, module_dir, "js-bindings", "prebuilt", platform)
            lib_binding_path = os.path.relpath(lib_binding_path, proj_path)
            libs_info[lib_binding] = lib_binding_path

        elif self._project._is_lua_project() and module_info.has_key(CCPluginModules.KEY_MODULE_LUA_BINDINGS):
            lib_name = module_info[CCPluginModules.KEY_MODULE_LUA_BINDINGS][CCPluginModules.KEY_MODULE_LUA_LIB_NAME]
            lib_binding = "%s%s%s" % (lib_name, platform_surfix[platform], self.get_platform_cfg(platform, CCPluginModules.KEY_CFG_LIB_EXT))
            lib_binding_path = os.path.join(self.engine_dir, module_dir, "lua-bindings", "prebuilt", platform)
            lib_binding_path = os.path.relpath(lib_binding_path, proj_path)
            libs_info[lib_binding] = lib_binding_path

        return libs_info

    def get_script_paths(self, language, module_name, paths=None):
        if paths is None:
            paths = []

        if module_name in CCPluginModules.CONSTANT_MODULES:
            return paths

        module_info = self.get_module_info(module_name)

        # add the depend modules script
        if module_info.has_key(CCPluginModules.KEY_MODULE_DEPEND_MODULES):
            for d in module_info[CCPluginModules.KEY_MODULE_DEPEND_MODULES]:
                paths = self.get_script_paths(language, d, paths=paths)

        # gather the script files path
        module_dir = module_info[CCPluginModules.KEY_MODULE_TARGET_DIR]
        script_path = os.path.join(self.engine_dir, module_dir, "%s-bindings" % language, "script")
        if os.path.exists(script_path) and (script_path not in paths):
            paths.append(script_path)

        return paths

    def gather_delta_info(self, is_remove):
        if is_remove:
            module_list = self.need_remove_modules
        else:
            module_list = self.need_add_modules

        delta_info = self.init_delta_info()
        for m in module_list:
            module_info = self.get_module_info(m)
            if module_info is None:
                cocos.Logging.warning("Can't find information of module '%s'." % m)
                continue

            # get the delta info of android platform
            if self.is_support_platform(cocos_project.Platforms.ANDROID, m):
                # gather the android delta info
                (android_lib, android_lib_path) = self.get_android_delta_info(module_info)
                delta_info[CCPluginModules.KEY_DELTA_ANDROID_LIBS][android_lib] = android_lib_path

            # get the delta info of win32, ios & mac platforms
            platforms = [
                cocos_project.Platforms.IOS,
                cocos_project.Platforms.MAC,
                cocos_project.Platforms.WIN32,
            ]
            for p in platforms:
                delta_key = self.get_platform_cfg(p, CCPluginModules.KEY_CFG_LIB_DELTA_KAY)
                if self.is_support_platform(p, m):
                    delta_info[delta_key] = self.get_delta_info(m, p, libs_info=delta_info[delta_key])

            if self._project._is_lua_project():
                delta_info[CCPluginModules.KEY_DELTA_LUA_PATHS] = self.get_script_paths("lua", m, delta_info[CCPluginModules.KEY_DELTA_LUA_PATHS])

            if self._project._is_js_project():
                delta_info[CCPluginModules.KEY_DELTA_JS_PATHS] = self.get_script_paths("js", m, delta_info[CCPluginModules.KEY_DELTA_JS_PATHS])

        return delta_info

    def remove_ios_mac_libs(self, proj_obj, libs_info, target_name):
        for lib in libs_info.keys():
            lib_path = libs_info[lib]
            remove_lib_path = os.path.join(lib_path, lib)
            proj_obj.remove_file_by_path(remove_lib_path)
            lib_name, lib_ext = os.path.splitext(lib)
            if lib_ext != ".dylib":
                proj_obj.remove_library_search_paths(lib_path, target_name=target_name)

    def add_ios_mac_libs(self, proj_obj, libs_info, target_name, parent_group):
        for lib in libs_info.keys():
            lib_path = libs_info[lib]
            lib_rel_path = os.path.join(str(lib_path), lib)
            lib_name, lib_ext = os.path.splitext(lib)
            if lib_ext == ".dylib":
                parent = proj_obj.get_or_create_group("Frameworks")
                proj_obj.add_file_if_doesnt_exist(lib_rel_path, parent=parent, tree="SDKROOT", target=target_name)
            else:
                proj_obj.add_file_if_doesnt_exist(lib_rel_path, parent=parent_group, tree="<group>", target=target_name)
                proj_obj.add_library_search_paths(lib_path, target_name=target_name, recursive=False)

    def remove_ios_mac_scripts(self, remove_paths, language, proj_obj, proj_path):
        chech_file_ext = ".%s" % language
        for p in remove_paths:
            rel_path = os.path.relpath(p, proj_path)
            for f in os.listdir(p):
                file_name, file_ext = os.path.splitext(f)
                if file_ext != chech_file_ext:
                    continue

                file_path = os.path.join(rel_path, f)
                proj_obj.remove_file_by_path(file_path)

    def add_ios_mac_scripts(self, add_paths, language, proj_obj, proj_path):
        chech_file_ext = ".%s" % language
        parent_group_name = CCPluginModules.XCODE_LUA_GROUP if language == "lua" else CCPluginModules.XCODE_JS_GROUP
        parent_group = proj_obj.get_or_create_group(parent_group_name)
        for p in add_paths:
            rel_path = os.path.relpath(p, proj_path)
            for f in os.listdir(p):
                file_name, file_ext = os.path.splitext(f)
                if file_ext != chech_file_ext:
                    continue

                file_path = os.path.join(rel_path, f)
                proj_obj.add_file_if_doesnt_exist(file_path, parent=parent_group, tree="<group>")

    def modify_build_cfg(self, script_paths, cfg_file_path, is_remove):
        f = open(cfg_file_path)
        cfg_info = json.load(f)
        f.close()

        cfg_path = os.path.dirname(cfg_file_path)
        copy_cfgs = cfg_info["must_copy_resources"]

        need_remove = []
        need_add = []
        for p in script_paths:
            rel_path = os.path.relpath(p, cfg_path)
            add_flag = True
            for cfg in copy_cfgs:
                from_path = cfg["from"]
                if from_path == rel_path:
                    if is_remove:
                        need_remove.append(cfg)
                    else:
                        add_flag = False
                    break

            if add_flag and (not is_remove) and (rel_path not in need_add):
                need_add.append(rel_path)

        if len(need_remove) > 0:
            for obj in need_remove:
                copy_cfgs.remove(obj)

        if len(need_add) > 0:
            for rel_path in need_add:
                add_cfg = {
                    "from" : rel_path,
                    "to" : ""
                }
                copy_cfgs.append(add_cfg)

        f = open(cfg_file_path, "w")
        json.dump(cfg_info, f, sort_keys = True, indent = 4)
        f.close()

    def remove_modules(self):
        if len(self.need_remove_modules) <= 0:
            return

        delta_info = self.gather_delta_info(True)

        # modify xcode project
        ios_proj_file = None
        ios_proj_obj = None
        if self.available_platforms.has_key(cocos_project.Platforms.IOS):
            ios_proj, ios_proj_file = self.get_xcode_proj_info(cocos_project.Platforms.IOS)
            ios_proj_obj = modify_pbxproj.XcodeProject.Load(ios_proj_file)
            ios_proj_name = "%s iOS" % ios_proj
            self.remove_ios_mac_libs(ios_proj_obj, delta_info[CCPluginModules.KEY_DELTA_IOS_LIBS], ios_proj_name)

            if self._project._is_lua_project():
                lua_paths = delta_info[CCPluginModules.KEY_DELTA_LUA_PATHS]
                ios_proj_path = os.path.dirname(os.path.dirname(ios_proj_file))
                self.remove_ios_mac_scripts(lua_paths, "lua", ios_proj_obj, ios_proj_path)

            if self._project._is_js_project():
                js_paths = delta_info[CCPluginModules.KEY_DELTA_JS_PATHS]
                ios_proj_path = os.path.dirname(os.path.dirname(ios_proj_file))
                self.remove_ios_mac_scripts(js_paths, "js", ios_proj_obj, ios_proj_path)

        mac_proj_obj = None
        if self.available_platforms.has_key(cocos_project.Platforms.MAC):
            mac_proj, mac_proj_file = self.get_xcode_proj_info(cocos_project.Platforms.MAC)
            if ios_proj_file is not None and mac_proj_file == ios_proj_file:
                mac_proj_obj = ios_proj_obj
            else:
                mac_proj_obj = modify_pbxproj.XcodeProject.Load(mac_proj_file)

            mac_proj_name = "%s Mac" % mac_proj
            self.remove_ios_mac_libs(mac_proj_obj, delta_info[CCPluginModules.KEY_DELTA_MAC_LIBS], mac_proj_name)

            if mac_proj_obj != ios_proj_obj:
                if self._project._is_lua_project():
                    lua_paths = delta_info[CCPluginModules.KEY_DELTA_LUA_PATHS]
                    mac_proj_path = os.path.dirname(os.path.dirname(mac_proj_file))
                    self.remove_ios_mac_scripts(lua_paths, "lua", mac_proj_obj, mac_proj_path)

                if self._project._is_js_project():
                    js_paths = delta_info[CCPluginModules.KEY_DELTA_JS_PATHS]
                    mac_proj_path = os.path.dirname(os.path.dirname(mac_proj_file))
                    self.remove_ios_mac_scripts(js_paths, "js", mac_proj_obj, mac_proj_path)

        # modify Android.mk
        mk_obj = None
        if self.available_platforms.has_key(cocos_project.Platforms.ANDROID):
            android_cfg = self.available_platforms[cocos_project.Platforms.ANDROID]
            mk_file = os.path.join(android_cfg.proj_path, "jni", "Android.mk")
            mk_obj = modify_mk.AndroidMK(mk_file)
            for lib in delta_info[CCPluginModules.KEY_DELTA_ANDROID_LIBS].keys():
                lib_path = delta_info[CCPluginModules.KEY_DELTA_ANDROID_LIBS][lib]
                mk_obj.remove_lib(lib, lib_path)

            # modify the build-cfg.json for android platform
            if self._project._is_lua_project():
                lua_paths = delta_info[CCPluginModules.KEY_DELTA_LUA_PATHS]
                cfg_path = os.path.join(android_cfg.proj_path, CCPluginModules.BUILD_CFG_FILE_NAME)
                self.modify_build_cfg(lua_paths, cfg_path, True)

            if self._project._is_js_project():
                js_paths = delta_info[CCPluginModules.KEY_DELTA_JS_PATHS]
                cfg_path = os.path.join(android_cfg.proj_path, CCPluginModules.BUILD_CFG_FILE_NAME)
                self.modify_build_cfg(js_paths, cfg_path, True)

        # modify VS project
        vs_proj_obj = None
        if self.available_platforms.has_key(cocos_project.Platforms.WIN32):
            vs_proj_cfg = self.available_platforms[cocos_project.Platforms.WIN32]
            vs_proj_path = vs_proj_cfg.proj_path
            print("vs proj path : %s" % vs_proj_path)
            proj_name, proj_file_name = self.checkFileByExtention(".vcxproj", vs_proj_path)
            vs_proj_file = os.path.join(vs_proj_path, proj_file_name)
            vs_proj_obj = modify_vcxproj.VCXProject(vs_proj_file)
            for lib in delta_info[CCPluginModules.KEY_DELTA_WIN32_LIBS].keys():
                lib_path = delta_info[CCPluginModules.KEY_DELTA_WIN32_LIBS][lib]
                lib_path = lib_path.replace("/", "\\")
                vs_proj_obj.remove_lib(lib, lib_path)

        # save files
        if ios_proj_obj is not None and ios_proj_obj.modified:
            ios_proj_obj.save()

        if (mac_proj_obj is not None) and (mac_proj_obj != ios_proj_obj) and mac_proj_obj.modified:
            mac_proj_obj.save()

        if mk_obj is not None:
            mk_obj.save()

        if vs_proj_obj is not None:
            vs_proj_obj.save()

    def add_modules(self):
        if len(self.need_add_modules) <= 0:
            return

        delta_info = self.gather_delta_info(False)

        # modify xcode project
        ios_proj_file = None
        ios_proj_obj = None
        if self.available_platforms.has_key(cocos_project.Platforms.IOS):
            ios_proj, ios_proj_file = self.get_xcode_proj_info(cocos_project.Platforms.IOS)
            ios_proj_obj = modify_pbxproj.XcodeProject.Load(ios_proj_file)
            ios_proj_name = "%s iOS" % ios_proj
            parent_group = ios_proj_obj.get_or_create_group("ios-libs")
            self.add_ios_mac_libs(ios_proj_obj, delta_info[CCPluginModules.KEY_DELTA_IOS_LIBS], ios_proj_name, parent_group)

            if self._project._is_lua_project():
                lua_paths = delta_info[CCPluginModules.KEY_DELTA_LUA_PATHS]
                ios_proj_path = os.path.dirname(os.path.dirname(ios_proj_file))
                self.add_ios_mac_scripts(lua_paths, "lua", ios_proj_obj, ios_proj_path)

            if self._project._is_js_project():
                js_paths = delta_info[CCPluginModules.KEY_DELTA_JS_PATHS]
                ios_proj_path = os.path.dirname(os.path.dirname(ios_proj_file))
                self.add_ios_mac_scripts(js_paths, "js", ios_proj_obj, ios_proj_path)

        mac_proj_obj = None
        if self.available_platforms.has_key(cocos_project.Platforms.MAC):
            mac_proj, mac_proj_file = self.get_xcode_proj_info(cocos_project.Platforms.MAC)
            if ios_proj_file is not None and mac_proj_file == ios_proj_file:
                mac_proj_obj = ios_proj_obj
            else:
                mac_proj_obj = modify_pbxproj.XcodeProject.Load(mac_proj_file)

            mac_proj_name = "%s Mac" % mac_proj
            parent_group = ios_proj_obj.get_or_create_group("mac-libs")
            self.add_ios_mac_libs(mac_proj_obj, delta_info[CCPluginModules.KEY_DELTA_MAC_LIBS], mac_proj_name, parent_group)

            if mac_proj_obj != ios_proj_obj:
                if self._project._is_lua_project():
                    lua_paths = delta_info[CCPluginModules.KEY_DELTA_LUA_PATHS]
                    mac_proj_path = os.path.dirname(os.path.dirname(mac_proj_file))
                    self.add_ios_mac_scripts(lua_paths, "lua", mac_proj_obj, mac_proj_path)

                if self._project._is_js_project():
                    js_paths = delta_info[CCPluginModules.KEY_DELTA_JS_PATHS]
                    mac_proj_path = os.path.dirname(os.path.dirname(mac_proj_file))
                    self.add_ios_mac_scripts(js_paths, "js", mac_proj_obj, mac_proj_path)

        # modify Android.mk
        mk_obj = None
        if self.available_platforms.has_key(cocos_project.Platforms.ANDROID):
            android_cfg = self.available_platforms[cocos_project.Platforms.ANDROID]
            mk_file = os.path.join(android_cfg.proj_path, "jni", "Android.mk")
            mk_obj = modify_mk.AndroidMK(mk_file)
            for lib in delta_info[CCPluginModules.KEY_DELTA_ANDROID_LIBS].keys():
                lib_path = delta_info[CCPluginModules.KEY_DELTA_ANDROID_LIBS][lib]
                mk_obj.add_lib(lib, lib_path)

            # modify the build-cfg.json for android platform
            if self._project._is_lua_project():
                lua_paths = delta_info[CCPluginModules.KEY_DELTA_LUA_PATHS]
                cfg_path = os.path.join(android_cfg.proj_path, CCPluginModules.BUILD_CFG_FILE_NAME)
                self.modify_build_cfg(lua_paths, cfg_path, False)

            if self._project._is_js_project():
                js_paths = delta_info[CCPluginModules.KEY_DELTA_JS_PATHS]
                cfg_path = os.path.join(android_cfg.proj_path, CCPluginModules.BUILD_CFG_FILE_NAME)
                self.modify_build_cfg(js_paths, cfg_path, False)

        # modify VS project
        vs_proj_obj = None
        if self.available_platforms.has_key(cocos_project.Platforms.WIN32):
            vs_proj_cfg = self.available_platforms[cocos_project.Platforms.WIN32]
            vs_proj_path = vs_proj_cfg.proj_path
            print("vs proj path : %s" % vs_proj_path)
            proj_name, proj_file_name = self.checkFileByExtention(".vcxproj", vs_proj_path)
            vs_proj_file = os.path.join(vs_proj_path, proj_file_name)
            vs_proj_obj = modify_vcxproj.VCXProject(vs_proj_file)
            for lib in delta_info[CCPluginModules.KEY_DELTA_WIN32_LIBS].keys():
                lib_path = delta_info[CCPluginModules.KEY_DELTA_WIN32_LIBS][lib]
                lib_path = lib_path.replace("/", "\\")
                vs_proj_obj.add_lib(lib, lib_path)

        # save files
        if ios_proj_obj is not None and ios_proj_obj.modified:
            ios_proj_obj.save()

        if (mac_proj_obj is not None) and (mac_proj_obj != ios_proj_obj) and mac_proj_obj.modified:
            mac_proj_obj.save()

        if mk_obj is not None:
            mk_obj.save()

        if vs_proj_obj is not None:
            vs_proj_obj.save()

    def get_register_info(self, module_name, language, register_info):
        module_info = self.get_module_info(module_name)
        binding_key = CCPluginModules.KEY_MODULE_LUA_BINDINGS if language == "lua" else CCPluginModules.KEY_MODULE_JS_BINDINGS
        if module_info.has_key(binding_key):
            binding_info = module_info[binding_key]
            if binding_info.has_key(CCPluginModules.KEY_MODULE_BINDING_HEADERS):
                headers = binding_info[CCPluginModules.KEY_MODULE_BINDING_HEADERS]
                for h in headers:
                    if h not in register_info[CCPluginModules.KEY_MODULE_BINDING_HEADERS]:
                        register_info[CCPluginModules.KEY_MODULE_BINDING_HEADERS].append(h)

            if binding_info.has_key(CCPluginModules.KEY_MODULE_BINDING_REGISTERS):
                registers = binding_info[CCPluginModules.KEY_MODULE_BINDING_REGISTERS]
                for r in registers:
                    if r not in register_info[CCPluginModules.KEY_MODULE_BINDING_REGISTERS]:
                        register_info[CCPluginModules.KEY_MODULE_BINDING_REGISTERS].append(r)

        if module_info.has_key(CCPluginModules.KEY_MODULE_DEPEND_MODULES):
            for m in module_info[CCPluginModules.KEY_MODULE_DEPEND_MODULES]:
                register_info = self.get_register_info(m, language, register_info)

        return register_info

    def get_lua_header_content(self, register_info):
        lua_format = "// This file is auto generated by command 'cocos modules'\n\n"\
                     "#ifndef __LUA_TEMPLATE_RUNTIME_FRAMEWORKS_RUNTIME_SRC_CLASSES_LUA_MODULE_REGISTER_H__\n"\
                     "#define __LUA_TEMPLATE_RUNTIME_FRAMEWORKS_RUNTIME_SRC_CLASSES_LUA_MODULE_REGISTER_H__\n\n"\
                     "%s\n"\
                     "int lua_module_register(lua_State* L)\n"\
                     "{\n"\
                     "%s"\
                     "    return 1;\n"\
                     "}\n\n"\
                     "#endif  // __LUA_TEMPLATE_RUNTIME_FRAMEWORKS_RUNTIME_SRC_CLASSES_LUA_MODULE_REGISTER_H__\n"

        include_str = ""
        for h in register_info[CCPluginModules.KEY_MODULE_BINDING_HEADERS]:
            line = "#include \"%s\"\n" % h
            include_str += line

        regist_str = ""
        for r in register_info[CCPluginModules.KEY_MODULE_BINDING_REGISTERS]:
            line = "    %s(L);\n" % r
            regist_str += line

        file_content = lua_format % (include_str, regist_str)
        return file_content

    def gen_register_header(self, language):
        header_path = "frameworks/runtime-src/Classes/%s_module_register.h" % language
        header_path = os.path.join(self._project.get_project_dir(), header_path)

        register_info = {
            CCPluginModules.KEY_MODULE_BINDING_HEADERS: [],
            CCPluginModules.KEY_MODULE_BINDING_REGISTERS: []
        }
        for m in self.select_modules:
            register_info = self.get_register_info(m, language, register_info)

        file_content = None
        if language == "lua":
            file_content = self.get_lua_header_content(register_info)

        if file_content is not None:
            f = open(header_path, "w")
            f.write(file_content)
            f.close()

    def parse_modules(self):
        self.need_remove_modules = []
        for m in self.cur_modules:
            if not m in self.select_modules:
                self.need_remove_modules.append(m)

        self.need_add_modules = []
        for m in self.select_modules:
            if not m in self.cur_modules:
                self.need_add_modules.append(m)

    def update_modules(self):
        self.parse_modules()
        print("Need remove modules : %s" % self.need_remove_modules)
        print("Need add modules : %s" % self.need_add_modules)

        self.remove_modules()
        self.add_modules()

        if len(self.need_remove_modules) > 0 or len(self.need_add_modules) > 0:
            # generate the register header file for script project
            if self._project._is_lua_project():
                self.gen_register_header("lua")

            if self._project._is_js_project():
                self.gen_register_header("js")

            # write the new modules when modules changed
            self._project.write_proj_config(CCPluginModules.PROJ_CFG_KEY_MODULES, self.select_modules)

    def run(self, argv, dependencies):
        self.parse_args(argv)

        self.update_modules()
