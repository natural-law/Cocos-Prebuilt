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
import sys

LUA_TEMPLATE_PATH = "templates/lua-template-runtime"

IOS_PREBUILT_PATH = "prebuilt/ios"
MAC_PREBUILT_PATH = "prebuilt/mac"

WIN32_COPY_LIB_PATHS = [
    "external\glfw3\prebuilt\win32",
    "external\win32-specific\zlib\prebuilt",
    "external\win32-specific\icon\prebuilt",
    "external\win32-specific\gles\prebuilt"
]

class TemplateModifier(object):
    def __init__(self, engine_path):
        if os.path.isabs(engine_path):
            self.engine_path = engine_path
        else:
            self.engine_path = os.path.abspath(engine_path)

        self.template_path = os.path.join(self.engine_path, LUA_TEMPLATE_PATH)
        self.template_engine_path = os.path.join(self.template_path, "frameworks/cocos2d-x")

    def modify_xcode_proj(self, proj_file_path, language):
        proj_modifier_path = os.path.join(os.path.dirname(__file__), 'proj_modifier')
        sys.path.append(proj_modifier_path)

        import modify_pbxproj
        pbx_proj = modify_pbxproj.XcodeProject.Load(proj_file_path)
        xcode_proj_path = os.path.join(proj_file_path, os.path.pardir, os.path.pardir)

        if language == "cpp":
            targetName = "HelloCpp"
        elif language == "lua":
            targetName = "HelloLua"
        else:
            targetName = "HelloJavascript"
        ios_target_name = "%s iOS" % targetName
        mac_target_name = "%s Mac" % targetName

        # remove the target dependencies
        pbx_proj.remove_proj_reference("cocos2d_libs.xcodeproj")
        if language == "lua":
            pbx_proj.remove_proj_reference("cocos2d_lua_bindings.xcodeproj")

        # add libraries search path
        ios_template_prebuilt_path = os.path.join(self.template_engine_path, IOS_PREBUILT_PATH)
        pbx_proj.add_library_search_paths(os.path.relpath(ios_template_prebuilt_path, xcode_proj_path), target_name=ios_target_name, recursive=False)
        mac_template_prebuilt_path = os.path.join(self.template_engine_path, MAC_PREBUILT_PATH)
        pbx_proj.add_library_search_paths(os.path.relpath(mac_template_prebuilt_path, xcode_proj_path), target_name=mac_target_name, recursive=False)

        # add libraries for targets
        ios_lib_group = pbx_proj.get_or_create_group("ios-libs")
        ios_abs_prebuilt_path = os.path.join(self.engine_path, IOS_PREBUILT_PATH)
        for lib in os.listdir(ios_abs_prebuilt_path):
            libname, libext = os.path.splitext(lib)
            if libext != ".a":
                continue

            if language == "cpp" and (libname.find("lua") >= 0 or libname.find("js") >= 0):
                continue

            ios_lib_path = os.path.join(os.path.relpath(ios_template_prebuilt_path, xcode_proj_path), lib)
            pbx_proj.add_file_if_doesnt_exist(ios_lib_path, ios_lib_group, tree="<group>", target=ios_target_name)

        mac_lib_group = pbx_proj.get_or_create_group("mac-libs")
        mac_abs_prebuilt_path = os.path.join(self.engine_path, MAC_PREBUILT_PATH)
        for lib in os.listdir(mac_abs_prebuilt_path):
            libname, libext = os.path.splitext(lib)
            if libext != ".a":
                continue

            if language == "cpp" and (libname.find("lua") >= 0 or libname.find("js") >= 0):
                continue

            mac_lib_path = os.path.join(os.path.relpath(mac_template_prebuilt_path, xcode_proj_path), lib)
            pbx_proj.add_file_if_doesnt_exist(mac_lib_path, mac_lib_group, tree="<group>", target=mac_target_name)

        if pbx_proj.modified:
            pbx_proj.save()

    def modify_vs_proj(self, proj_file_path):
        print("modify vs proj file: %s" % proj_file_path)
        # proj_modifier_path = os.path.join(os.path.dirname(__file__), '..', 'console', 'plugins', "project_modules")
        # sys.path.append(proj_modifier_path)
        #
        # import modify_vcxproj
        # vcx_proj = modify_vcxproj.VCXProject(proj_file_path)
        #
        # # remove the project references
        # vcx_proj.remove_proj_reference()
        #
        # # set include paths
        # proj_include_paths = [
        #     "../Classes",
        #     "../Classes/runtime",
        #     "../Classes/protobuf-lite"
        # ]
        # ret_paths = []
        # for p in proj_include_paths:
        #     rel_path = "$(ProjectDir)%s" % p
        #     ret_paths.append(rel_path)
        #
        # for p in LUA_ALL_INCLUDE_PATHS:
        #     rel_path = "$(EngineRoot)%s" % p
        #     ret_paths.append(rel_path)
        #
        # vcx_proj.set_include_dirs(ret_paths)
        #
        # # modify the PreBuildEvent for copy scripts
        # scipt_paths = []
        # for m in self.select_modules:
        #     module_info = self.modules_info[m]
        #     if module_info.has_key(KEY_MODULE_LUA_BINDINGS):
        #         p = os.path.join(module_info[KEY_MODULE_TARGET_DIR], "lua-bindings/script")
        #         abs_path = os.path.join(self.engine_path, p)
        #         if os.path.exists(abs_path):
        #             scipt_paths.append(p)
        #
        # configs = [ "debug", "release" ]
        # for config in configs:
        #     prebuild_cmd = vcx_proj.get_event_command("PreBuildEvent", config)
        #     import io
        #     buf = io.StringIO(prebuild_cmd)
        #     newlines = []
        #
        #     # remove the old copy script command
        #     for cmd_line in buf.readlines():
        #         need_keep = True
        #         for check_str in LUA_CHECK_COPY_SCRIPT_PATHS:
        #             check_str = check_str.replace("/", "\\")
        #             temp_cmd = cmd_line.replace("/", "\\")
        #             if temp_cmd.find(check_str) > 0:
        #                 need_keep = False
        #                 break
        #
        #         if need_keep:
        #             newlines.append(cmd_line)
        #
        #     # add the new commands for copy scripts
        #     for p in scipt_paths:
        #         path = p.replace("/", "\\")
        #         cmd_line = "xcopy \"$(EngineRoot)%s\\*.lua\" \"$(LocalDebuggerWorkingDirectory)\" /e /Y\n" % path
        #         newlines.append(cmd_line)
        #
        #     new_cmds = "".join(newlines)
        #     vcx_proj.set_event_command("PreBuildEvent", new_cmds, config)
        #
        # # modify the PreLinkEvent for copy libraries
        # prebuilt_paths = []
        # for m in self.select_modules:
        #     prebuilt_paths = self.gather_module_prebuilt_path(m, prebuilt_paths)
        #
        # lib_paths = []
        # for p in WIN32_COPY_LIB_PATHS:
        #     lib_paths.append(p)
        #
        # for p in prebuilt_paths:
        #     lib_paths.append(os.path.join(p, "win32"))
        #
        # copy_libs_cmd = "if not exist \"$(OutDir)\" mkdir \"$(OutDir)\"\n"
        # for p in lib_paths:
        #     cmd_line = "xcopy /Y /Q \"$(EngineRoot)%s\\*.*\" \"$(OutDir)\"\n" % p
        #     cmd_line = cmd_line.replace("/", "\\")
        #     copy_libs_cmd += cmd_line
        #
        # vcx_proj.set_event_command("PreLinkEvent", copy_libs_cmd)
        #
        # vcx_proj.save()
