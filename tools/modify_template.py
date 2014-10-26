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

WIN32_LINK_CPP_LIBS = [
    "libbox2d", "libcocos2d", "libSpine"
]

WIN32_LINK_LUA_LIBS = [ "libluacocos2d" ]

WIN32_LINK_JS_LIBS = [
    "libJSBinding", "libJSBindingForBuilder", "libJSBindingForChipmunk",
    "libJSBindingForExtension", "libJSBindingForGui", "libJSBindingForLocalStorage",
    "libJSBindingForNetwork", "libJSBindingForSpine", "libJSBindingForStudio"
]

XCODE_LINK_CPP_LIBS = [
    "libcocos2d"
]

XCODE_LINK_LUA_LIBS = [ "libluacocos2d" ]

XCODE_LINK_JS_LIBS = [ "libjsbindings" ]

class TemplateModifier(object):
    def __init__(self, engine_path):
        if os.path.isabs(engine_path):
            self.engine_path = engine_path
        else:
            self.engine_path = os.path.abspath(engine_path)

    def modify_xcode_proj(self, proj_file_path, language):
        proj_modifier_path = os.path.join(os.path.dirname(__file__), 'proj_modifier')
        sys.path.append(proj_modifier_path)

        import modify_pbxproj
        pbx_proj = modify_pbxproj.XcodeProject.Load(proj_file_path)

        if language == "cpp":
            targetName = "HelloCpp"
            engine_path = "/Applications/Cocos/frameworks/cocos2d-x"
            link_libs = XCODE_LINK_CPP_LIBS
            old_engine_path = "$(SRCROOT)/../cocos2d"
            xcode_proj_path = os.path.join(self.engine_path, "templates/cpp-template-default/proj.ios_mac")
        elif language == "lua":
            targetName = "HelloLua"
            engine_path = "/Applications/Cocos/frameworks/cocos2d-x"
            link_libs = XCODE_LINK_CPP_LIBS + XCODE_LINK_LUA_LIBS
            old_engine_path = "$(SRCROOT)/../../cocos2d-x"
            xcode_proj_path = os.path.join(self.engine_path, "templates/lua-template-runtime/frameworks/runtime-src/proj.ios_mac")
        else:
            targetName = "HelloJavascript"
            engine_path = "/Applications/Cocos/frameworks/cocos2d-js"
            link_libs = XCODE_LINK_CPP_LIBS + XCODE_LINK_JS_LIBS
            old_engine_path = "$(SRCROOT)/../../cocos2d-js"
            xcode_proj_path = os.path.join(self.engine_path, "templates/js-template-runtime/frameworks/runtime-src/proj.ios_mac")
        ios_target_name = "%s iOS" % targetName
        mac_target_name = "%s Mac" % targetName

        # remove the target dependencies
        pbx_proj.remove_proj_reference("cocos2d_libs.xcodeproj")
        if language == "lua":
            pbx_proj.remove_proj_reference("cocos2d_lua_bindings.xcodeproj")

        # add libraries search path
        ios_template_prebuilt_path = os.path.join(engine_path, IOS_PREBUILT_PATH)
        pbx_proj.add_library_search_paths(ios_template_prebuilt_path, target_name=ios_target_name, recursive=False)
        mac_template_prebuilt_path = os.path.join(engine_path, MAC_PREBUILT_PATH)
        pbx_proj.add_library_search_paths(mac_template_prebuilt_path, target_name=mac_target_name, recursive=False)

        # add libraries for targets
        ios_lib_group = pbx_proj.get_or_create_group("ios-libs")
        mac_lib_group = pbx_proj.get_or_create_group("mac-libs")
        for lib in link_libs:
            ios_lib_name = "%s iOS.a" % lib
            mac_lib_name = "%s Mac.a" % lib
            ios_lib_path = os.path.join(ios_template_prebuilt_path, ios_lib_name)
            pbx_proj.add_file_if_doesnt_exist(ios_lib_path, ios_lib_group, tree="<group>", target=ios_target_name)

            mac_lib_path = os.path.join(mac_template_prebuilt_path, mac_lib_name)
            pbx_proj.add_file_if_doesnt_exist(mac_lib_path, mac_lib_group, tree="<group>", target=mac_target_name)

        # add studio resources to the xcode project of cpp template
        if language == "cpp":
            pbx_proj.remove_file_by_path("CloseNormal.png")
            pbx_proj.remove_file_by_path("CloseSelected.png")
            pbx_proj.remove_file_by_path("HelloWorld.png")
            pbx_proj.remove_file_by_path("Marker Felt.ttf")
            pbx_proj.remove_file_by_path("fonts")
            pbx_proj.remove_file_by_path("res")

            pbx_proj.remove_group_by_path("../Resources")
            pbx_proj.add_file_if_doesnt_exist("../Resources", tree="<group>")
            # res_group = pbx_proj.get_or_create_group("Resources")
            # pbx_proj.add_file_if_doesnt_exist("MainScene.csb", res_group, tree="<group>")
            # pbx_proj.add_file_if_doesnt_exist("iphone", res_group, tree="<group>")

        if pbx_proj.modified:
            pbx_proj.save()

        # modify the engine path
        f = open(proj_file_path)
        file_content = f.read()
        f.close()

        file_content = file_content.replace(old_engine_path, engine_path)
        f = open(proj_file_path, "w")
        f.write(file_content)
        f.close()

    def modify_vs_proj(self, proj_file_path, language):
        proj_modifier_path = os.path.join(os.path.dirname(__file__), "proj_modifier")
        sys.path.append(proj_modifier_path)

        import modify_vcxproj
        vcx_proj = modify_vcxproj.VCXProject(proj_file_path)

        # remove the project references
        vcx_proj.remove_proj_reference()

        replace_strs = [ "$(EngineRoot)" ]
        if language == "cpp":
            link_libs = WIN32_LINK_CPP_LIBS
            engine_root = "$(COCOS_X_ROOT)"
            replace_strs.append("..\cocos2d")
        elif language == "lua":
            link_libs = WIN32_LINK_CPP_LIBS + WIN32_LINK_LUA_LIBS
            engine_root = "$(COCOS_X_ROOT)"
            replace_strs.append("..\..\cocos2d-x")
        else:
            link_libs = WIN32_LINK_CPP_LIBS + WIN32_LINK_JS_LIBS
            engine_root = "$(COCOS_JS_ROOT)"

        # for lib in link_libs:
        #     lib_name = "%s.lib" % lib
        #     vcx_proj.add_lib(lib_name)

        copy_libs_cmd = "if not exist \"$(OutDir)\" mkdir \"$(OutDir)\"\n" \
                        "xcopy /Y /Q \"$(EngineRoot)prebuilt\\win32\\*.*\" \"$(OutDir)\"\n"
        vcx_proj.set_event_command("PreLinkEvent", copy_libs_cmd)

        vcx_proj.remove_predefine_macro("_DEBUG")

        vcx_proj.save()

        f = open(proj_file_path)
        file_content = f.read()
        f.close()

        if language == "lua":
            # replace the "lua\lua;" to "lua\luajit;"
            file_content = file_content.replace("lua\\lua;", "lua\\luajit\\include;")

        file_content = file_content.replace("MultiThreadedDebugDLL", "MultiThreadedDLL")
        for str in replace_strs:
            file_content = file_content.replace(str, "%s\\" % engine_root)
        f = open(proj_file_path, "w")
        f.write(file_content)
        f.close()

        # modify the Runtime.cpp
        vcx_proj_path = os.path.dirname(proj_file_path)
        cpp_path = os.path.join(vcx_proj_path, os.path.pardir, "Classes/runtime/Runtime.cpp")
        if os.path.exists(cpp_path):
            f = open(cpp_path)
            file_content = f.read()
            f.close()

            file_content = file_content.replace("#ifndef _DEBUG", "#ifndef COCOS2D_DEBUG")
            f = open(cpp_path, "w")
            f.write(file_content)
            f.close()
