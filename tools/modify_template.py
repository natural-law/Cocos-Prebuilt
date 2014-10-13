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
    "libAudio", "libBox2D", "libchipmunk",
    "libcocos2d", "libCocosBuilder", "libCocosStudio",
    "libExtensions", "libGUI", "libLocalStorage",
    "libNetwork", "libSpine"
]

WIN32_LINK_LUA_LIBS = [ "liblua" ]

WIN32_LINK_JS_LIBS = [
    "libJSBinding", "libJSBindingForBuilder", "libJSBindingForChipmunk",
    "libJSBindingForExtension", "libJSBindingForGui", "libJSBindingForLocalStorage",
    "libJSBindingForNetwork", "libJSBindingForSpine", "libJSBindingForStudio"
]

XCODE_LINK_CPP_LIBS = [
    "libCocosDenshion", "libchipmunk", "libcocos2dx-extensions",
    "libbox2d", "libcocos2dx"
]

XCODE_LINK_LUA_LIBS = [ "libluabindings" ]

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
            template_engine_path = os.path.join(self.engine_path, "templates/cpp-template-default/cocos2d")
            link_libs = XCODE_LINK_CPP_LIBS
            xcode_proj_path = os.path.join(self.engine_path, "templates/cpp-template-default/proj.ios_mac")
        elif language == "lua":
            targetName = "HelloLua"
            template_engine_path = os.path.join(self.engine_path, "templates/lua-template-runtime/frameworks/cocos2d-x")
            link_libs = XCODE_LINK_CPP_LIBS + XCODE_LINK_LUA_LIBS
            xcode_proj_path = os.path.join(self.engine_path, "templates/lua-template-runtime/frameworks/runtime-src/proj.ios_mac")
        else:
            targetName = "HelloJavascript"
            template_engine_path = os.path.join(self.engine_path, "templates/js-template-runtime/frameworks/js-bindings")
            link_libs = XCODE_LINK_CPP_LIBS + XCODE_LINK_JS_LIBS
            xcode_proj_path = os.path.join(self.engine_path, "templates/js-template-runtime/frameworks/runtime-src/proj.ios_mac")
        ios_target_name = "%s iOS" % targetName
        mac_target_name = "%s Mac" % targetName

        # remove the target dependencies
        pbx_proj.remove_proj_reference("cocos2d_libs.xcodeproj")
        if language == "lua":
            pbx_proj.remove_proj_reference("cocos2d_lua_bindings.xcodeproj")

        # add libraries search path
        ios_template_prebuilt_path = os.path.join(template_engine_path, IOS_PREBUILT_PATH)
        pbx_proj.add_library_search_paths(os.path.relpath(ios_template_prebuilt_path, xcode_proj_path), target_name=ios_target_name, recursive=False)
        mac_template_prebuilt_path = os.path.join(template_engine_path, MAC_PREBUILT_PATH)
        pbx_proj.add_library_search_paths(os.path.relpath(mac_template_prebuilt_path, xcode_proj_path), target_name=mac_target_name, recursive=False)

        # add libraries for targets
        ios_lib_group = pbx_proj.get_or_create_group("ios-libs")
        mac_lib_group = pbx_proj.get_or_create_group("mac-libs")
        for lib in link_libs:
            ios_lib_name = "%s iOS.a" % lib
            mac_lib_name = "%s Mac.a" % lib
            ios_lib_path = os.path.join(os.path.relpath(ios_template_prebuilt_path, xcode_proj_path), ios_lib_name)
            pbx_proj.add_file_if_doesnt_exist(ios_lib_path, ios_lib_group, tree="<group>", target=ios_target_name)

            mac_lib_path = os.path.join(os.path.relpath(mac_template_prebuilt_path, xcode_proj_path), mac_lib_name)
            pbx_proj.add_file_if_doesnt_exist(mac_lib_path, mac_lib_group, tree="<group>", target=mac_target_name)

        # add studio resources to the xcode project of cpp template
        if language == "cpp":
            pbx_proj.remove_file_by_path("CloseNormal.png")
            pbx_proj.remove_file_by_path("CloseSelected.png")
            pbx_proj.remove_file_by_path("HelloWorld.png")

            res_group = pbx_proj.get_or_create_group("Resources")
            pbx_proj.add_file_if_doesnt_exist("MainScene.csb", res_group, tree="<group>")
            pbx_proj.add_file_if_doesnt_exist("iphone/CloseNormal.png", res_group, tree="<group>")
            pbx_proj.add_file_if_doesnt_exist("iphone/CloseSelected.png", res_group, tree="<group>")
            pbx_proj.add_file_if_doesnt_exist("iphone/HelloWorld.png", res_group, tree="<group>")

        if pbx_proj.modified:
            pbx_proj.save()

    def modify_vs_proj(self, proj_file_path, language):
        proj_modifier_path = os.path.join(os.path.dirname(__file__), "proj_modifier")
        sys.path.append(proj_modifier_path)

        import modify_vcxproj
        vcx_proj = modify_vcxproj.VCXProject(proj_file_path)

        # remove the project references
        vcx_proj.remove_proj_reference()

        if language == "cpp":
            link_libs = WIN32_LINK_CPP_LIBS
        elif language == "lua":
            link_libs = WIN32_LINK_CPP_LIBS + WIN32_LINK_LUA_LIBS
        else:
            link_libs = WIN32_LINK_CPP_LIBS + WIN32_LINK_JS_LIBS

        for lib in link_libs:
            lib_name = "%s.lib" % lib
            vcx_proj.add_lib(lib_name)

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
