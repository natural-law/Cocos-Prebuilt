#!/usr/bin/python
# ----------------------------------------------------------------------------
# modify the runtime template for prebuilt engine
#
# Copyright 2014 (C) zhangbin
#
# License: MIT
# ----------------------------------------------------------------------------
'''
modify the runtime template for prebuilt engine
'''

import os
import json
import re
import sys

from argparse import ArgumentParser

LUA_MODIFY_FILES = {
    "cocos-project-template.json" : "modify_template_json",
    "frameworks/runtime-src/Classes/lua_module_register.h" : "modify_register",
    "frameworks/runtime-src/proj.android/build-cfg.json" : "modify_build_config",
    "frameworks/runtime-src/proj.android/project.properties" : "modify_project_properties",
    "frameworks/runtime-src/proj.android/jni/Android.mk" : "modify_android_mk",
    "frameworks/runtime-src/proj.ios_mac/HelloLua.xcodeproj/project.pbxproj" : "modify_xcode_proj",
    "frameworks/runtime-src/proj.win32/build-cfg.json" : "modify_build_config",
    "frameworks/runtime-src/proj.win32/HelloLua.vcxproj" : "modify_vs_proj"
}

LUA_ALL_INCLUDE_PATHS = [
    "cocos/include", "cocos/lua-bindings/include",
    "external", "external/lua/luajit/include",
    "modules/chipmunk/include", "modules/Box2D/include",
    "modules/audio/include", "modules/audio/lua-bindings/include",
    "modules/cocosbuilder/include", "modules/cocosbuilder/lua-bindings/include",
    "modules/cocostudio/include", "modules/cocostudio/lua-bindings/include",
    "modules/extensions/include", "modules/extensions/lua-bindings/include",
    "modules/network/include", "modules/network/lua-bindings/include",
    "modules/spine/include", "modules/spine/lua-bindings/include",
    "modules/ui/include", "modules/ui/lua-bindings/include"
]

LUA_CHECK_COPY_SCRIPT_PATHS = [
    "cocos/scripting/lua-bindings/script",
    "external/lua/luasocket"
]

LUA_TEMPLATE_PATH = "templates/lua-template-runtime"

KEY_MODULE_WIN32_LIB_FILE_NAME = "win32_lib_file_name"
KEY_MODULE_IOS_LIB_FILE_NAME = "ios_lib_file_name"
KEY_MODULE_MAC_LIB_FILE_NAME = "mac_lib_file_name"
KEY_MODULE_TARGET_DIR = "target_dir"
KEY_MODULE_LUA_BINDINGS = "lua_bindings"
KEY_MODULE_LUA_LIB_NAME = "lua_lib_name"

class LuaModifier(object):
    def __init__(self, engine_path):
        if os.path.isabs(engine_path):
            self.engine_path = engine_path
        else:
            self.engine_path = os.path.abspath(engine_path)

        self.template_path = os.path.join(self.engine_path, LUA_TEMPLATE_PATH)
        self.template_engine_path = os.path.join(self.template_path, "frameworks/cocos2d-x")
        self.parse_module_info()

    def parse_module_info(self):
        f = open(os.path.join(self.engine_path, "modules-info.json"))
        self.modules_info = json.load(f)
        f.close()

        f = open(os.path.join(self.template_path, ".cocos-project.json"))
        info = json.load(f)
        self.select_modules = info["modules"]
        f.close()

        self.select_modules.insert(0, "cocos2d")

    def do_modify(self):
        for key in LUA_MODIFY_FILES.keys():
            func_name = LUA_MODIFY_FILES[key]
            func = getattr(self, func_name)

            file_path = os.path.join(self.template_path, key)
            func(file_path)

    def get_remove_copy_cfgs(self, copy_cfgs):
        need_remove = []
        for item in copy_cfgs:
            from_path = item["from"]
            for check_str in LUA_CHECK_COPY_SCRIPT_PATHS:
                if from_path.find(check_str) >= 0:
                    need_remove.append(item)

        return need_remove

    def modify_template_json(self, json_path):
        f = open(json_path)
        cfg_info = json.load(f)
        f.close()

        # remove the copy script configs
        modify_cfg = cfg_info["do_default"]["append_dir"]
        need_remove = self.get_remove_copy_cfgs(modify_cfg)

        for item in need_remove:
            modify_cfg.remove(item)

        # add copy script configs
        to_dirs = [
            "runtime/mac/PrebuiltRuntimeLua.app/Contents/Resources",
            "runtime/ios/PrebuiltRuntimeLua.app",
            "runtime/win32"
        ]
        for m in self.select_modules:
            module_info = self.modules_info[m]
            target_dir = module_info[KEY_MODULE_TARGET_DIR]
            from_path = os.path.join(target_dir, "lua-bindings/script")

            # if the script path not existed, continue
            abs_path = os.path.join(self.engine_path, from_path)
            if not os.path.exists(abs_path):
                continue

            for to_dir in to_dirs:
                cfg = {
                    "from": from_path,
                    "to": to_dir,
                    "include": [
                        "*.lua"
                    ]
                }
                modify_cfg.append(cfg)

        f = open(json_path, "w")
        json.dump(cfg_info, f, sort_keys = True, indent = 4)
        f.close()

    def modify_register(self, register_path):
        f = open(register_path)
        lines = f.readlines()
        f.close()

        pattern = r"^#include[ \t]+\"(.*)/.*"
        line_idx = 0
        for line in lines:
            str_line = line.lstrip()
            match_obj = re.match(pattern, str_line)
            if match_obj:
                folder_name = match_obj.group(1)
                str_replaced = line.replace("%s/" % folder_name, "")
                lines[line_idx] = str_replaced

            line_idx += 1

        f = open(register_path, "w")
        file_content = "".join(lines)
        f.write(file_content)
        f.close()

    def modify_build_config(self, cfg_path):
        f = open(cfg_path)
        cfg_info = json.load(f)
        f.close()

        # remove the copy script configs
        modify_cfg = cfg_info["must_copy_resources"]
        need_remove = self.get_remove_copy_cfgs(modify_cfg)

        for item in need_remove:
            modify_cfg.remove(item)

        # add copy script configs
        cfg_dir = os.path.dirname(cfg_path)

        for m in self.select_modules:
            module_info = self.modules_info[m]
            target_dir = module_info[KEY_MODULE_TARGET_DIR]
            script_dir = os.path.join(target_dir, "lua-bindings/script")

            # if the script path not existed, continue
            abs_path = os.path.join(self.engine_path, script_dir)
            if not os.path.exists(abs_path):
                continue

            script_path = os.path.join(self.template_engine_path, script_dir)
            rel_path = os.path.relpath(script_path, cfg_dir)
            cfg = {
                "from": rel_path,
                "to": "",
                "include": [
                    "*.lua"
                ]
            }
            modify_cfg.append(cfg)

        # modify the ndk module path
        if cfg_info.has_key("ndk_module_path"):
            cfg_info["ndk_module_path"] = [
                "../../cocos2d-x"
            ]

        f = open(cfg_path, "w")
        json.dump(cfg_info, f, sort_keys = True, indent = 4)
        f.close()

    def modify_project_properties(self, file_path):
        f = open(file_path)
        lines = f.readlines()
        f.close()

        path_before = "cocos2d-x/cocos/platform/android/java"
        path_new = "cocos2d-x/cocos/include/platform/android/java"
        new_lines = []
        for line in lines:
            new_line = line.replace(path_before, path_new)
            new_lines.append(new_line)

        f = open(file_path, "w")
        file_content = "".join(new_lines)
        f.write(file_content)
        f.close()

    def modify_android_mk(self, mk_path):
        f = open(mk_path)
        lines = f.readlines()
        f.close()

        # remove the script call-import
        check_path = "scripting/lua-bindings/proj.android"
        new_lines = []
        insert_index = -1
        cur_index = 0
        pattern = r"^\$\(call[ \t]*import-module,[ \t]*(.*)\)"
        for line in lines:
            lstrip_str = line.lstrip()
            match_obj = re.match(pattern, lstrip_str)
            if match_obj:
                get_path = match_obj.group(1)
                if get_path == check_path:
                    insert_index = cur_index
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

            cur_index += 1

        # generate the script call-import
        insert_str = ""
        for m in self.select_modules:
            module_path = self.modules_info[m][KEY_MODULE_TARGET_DIR]
            import_path = os.path.join(module_path, "lua-bindings/prebuilt/android")
            call_import = "$(call import-module, %s)\n" % import_path
            insert_str += call_import

        if insert_index >= 0:
            new_lines.insert(insert_index, insert_str)
        else:
            new_lines.append(insert_str)

        f = open(mk_path, "w")
        file_content = "".join(new_lines)
        f.write(file_content)
        f.close()

    def modify_xcode_proj(self, proj_file_path):
        proj_modifier_path = os.path.join(os.path.dirname(__file__), '..', 'console', 'plugins', "project_modules")
        sys.path.append(proj_modifier_path)

        import modify_pbxproj
        pbx_proj = modify_pbxproj.XcodeProject.Load(proj_file_path)

        # remove the target dependencies
        pbx_proj.remove_proj_reference("cocos2d_libs.xcodeproj")
        pbx_proj.remove_proj_reference("cocos2d_lua_bindings.xcodeproj")

        # remove user header search path
        pbx_proj.remove_user_header_search_paths("ALL", "PROJECT")
        pbx_proj.remove_user_header_search_paths("../../cocos2d-x/cocos/platform/ios", "HelloLua iOS")
        pbx_proj.remove_user_header_search_paths("../../cocos2d-x/cocos/platform/mac", "HelloLua Mac")

        # remove the lua common group
        lua_group = pbx_proj.get_group_id("Lua Common")
        pbx_proj.remove_group(lua_group)

        # add user header search path
        xcode_proj_path = os.path.dirname(os.path.dirname(proj_file_path))
        header_paths = []
        for p in LUA_ALL_INCLUDE_PATHS:
            include_path = os.path.join(self.template_engine_path, p)
            rel_path = os.path.relpath(include_path, xcode_proj_path)
            header_paths.append(rel_path)
        pbx_proj.add_user_header_search_paths(header_paths, "PROJECT", recursive=False)
        pbx_proj.add_user_header_search_paths("../../cocos2d-x/cocos/include/platform/ios", "HelloLua iOS", recursive=False)
        pbx_proj.add_user_header_search_paths("../../cocos2d-x/cocos/include/platform/mac", "HelloLua Mac", recursive=False)

        # add libraries for targets
        ios_lib_group = pbx_proj.get_or_create_group("ios-libs")
        mac_lib_group = pbx_proj.get_or_create_group("mac-libs")
        lua_group = pbx_proj.get_or_create_group("Lua Common")
        for m in self.select_modules:
            module_info = self.modules_info[m]
            module_dir = module_info[KEY_MODULE_TARGET_DIR]
            module_abs_path = os.path.join(self.template_engine_path, module_dir)
            module_rel_path = os.path.relpath(module_abs_path, xcode_proj_path)
            if module_info.has_key(KEY_MODULE_IOS_LIB_FILE_NAME):
                ios_lib_path = os.path.join(module_rel_path, "prebuilt/ios", module_info[KEY_MODULE_IOS_LIB_FILE_NAME])
                pbx_proj.add_file_if_doesnt_exist(ios_lib_path, ios_lib_group, tree="<group>", target="HelloLua iOS")
                pbx_proj.add_library_search_paths(os.path.dirname(ios_lib_path), target_name="HelloLua iOS", recursive=False)

            if module_info.has_key(KEY_MODULE_MAC_LIB_FILE_NAME):
                mac_lib_path = os.path.join(module_rel_path, "prebuilt/mac", module_info[KEY_MODULE_MAC_LIB_FILE_NAME])
                pbx_proj.add_file_if_doesnt_exist(mac_lib_path, mac_lib_group, tree="<group>", target="HelloLua Mac")
                pbx_proj.add_library_search_paths(os.path.dirname(mac_lib_path), target_name="HelloLua Mac", recursive=False)

            if module_info.has_key(KEY_MODULE_LUA_BINDINGS):
                lua_bindings_info = module_info[KEY_MODULE_LUA_BINDINGS]
                lua_lib_name = lua_bindings_info[KEY_MODULE_LUA_LIB_NAME]
                lua_ios_lib_path = os.path.join(module_rel_path, "lua-bindings/prebuilt/ios", "%s iOS.a" % lua_lib_name)
                lua_mac_lib_path = os.path.join(module_rel_path, "lua-bindings/prebuilt/mac", "%s Mac.a" % lua_lib_name)
                pbx_proj.add_file_if_doesnt_exist(lua_ios_lib_path, ios_lib_group, tree="<group>", target="HelloLua iOS")
                pbx_proj.add_file_if_doesnt_exist(lua_mac_lib_path, mac_lib_group, tree="<group>", target="HelloLua Mac")
                pbx_proj.add_library_search_paths(os.path.dirname(lua_ios_lib_path), target_name="HelloLua iOS", recursive=False)
                pbx_proj.add_library_search_paths(os.path.dirname(lua_mac_lib_path), target_name="HelloLua Mac", recursive=False)

                lua_script_path = os.path.join(self.engine_path, module_dir, "lua-bindings/script")
                if os.path.exists(lua_script_path):
                    for f in os.listdir(lua_script_path):
                        f_name, f_ext = os.path.splitext(f)
                        if f_ext != ".lua":
                            continue

                        lua_rel_path = os.path.join(module_rel_path, "lua-bindings/script", f)
                        pbx_proj.add_file_if_doesnt_exist(lua_rel_path, lua_group, tree="<group>")

        if pbx_proj.modified:
            pbx_proj.save()

    def modify_vs_proj(self, proj_file_path):
        proj_modifier_path = os.path.join(os.path.dirname(__file__), '..', 'console', 'plugins', "project_modules")
        sys.path.append(proj_modifier_path)

        import modify_vcxproj
        vcx_proj = modify_vcxproj.VCXProject(proj_file_path)

        # remove the project references
        vcx_proj.remove_proj_reference()

        vcx_proj.save()

if __name__ == "__main__":
    parser = ArgumentParser(description="Generate prebuilt engine for Cocos Engine.")
    parser.add_argument('-x', "--cocos2dx", dest='x_engine_path', required=True, help='Set the path of cocos2d-x.')
    # parser.add_argument('-j', "--cocos2djs", dest='js_engine_path', help='Set the path of cocos2d-js.')
    (args, unknown) = parser.parse_known_args()

    if len(unknown) > 0:
        print("unknown arguments: %s" % unknown)

    modifier = LuaModifier(args.x_engine_path)
    modifier.do_modify()
