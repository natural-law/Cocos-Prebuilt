#!/usr/bin/python
# ----------------------------------------------------------------------------
# generate the prebuilt Android.mk from source code Android.mk
#
# Copyright 2014 (C) zhangbin
#
# License: MIT
# ----------------------------------------------------------------------------
'''
generate the prebuilt Android.mk from source code Android.mk
'''

import os
import shutil
import re

from argparse import ArgumentParser

class MKGenerator(object):

    SRC_FILE_CFG_PATTERN = r"^LOCAL_SRC_FILES[ ]+\:=[ ]+.+"
    INCLUDE_CFG_PATTERN  = r"^include[ ]+\$\(BUILD_STATIC_LIBRARY\)"

    LIB_MODULE_PATTERN = r"^LOCAL_MODULE[ ]+\:=[ ]+(.+)"
    LIB_MODULE_FILENAME_PATTERN   = r"^LOCAL_MODULE_FILENAME[ ]+\:=[ ]+(.+)"

    def __init__(self, src_mk_path, lib_file_path, dst_mk_path=None):
        if os.path.isabs(src_mk_path):
            self.src_mk_path = src_mk_path
        else:
            self.src_mk_path = os.path.abspath(src_mk_path)

        if os.path.isabs(lib_file_path):
            self.lib_file_path = lib_file_path
        else:
            self.lib_file_path = os.path.abspath(lib_file_path)

        if dst_mk_path is None:
            self.dst_mk_path = os.path.join(os.path.dirname(src_mk_path), "Android-prebuilt.mk")
        else:
            if os.path.isabs(dst_mk_path):
                self.dst_mk_path = dst_mk_path
            else:
                self.dst_mk_path = os.path.abspath(dst_mk_path)

    def get_lib_file_name(self):
        src_mk_obj = open(self.src_mk_path)
        module_file_name = None
        module_name = None
        for line in src_mk_obj.readlines():
            trim_line = line.lstrip(" ")
            trim_line = trim_line.rstrip(" ")
            match1 = re.match(MKGenerator.LIB_MODULE_FILENAME_PATTERN, trim_line)
            if match1 is not None:
                module_file_name = match1.group(1)

            match2 = re.match(MKGenerator.LIB_MODULE_PATTERN, trim_line)
            if match2 is not None:
                module_name = match2.group(1)

        ret = None
        if module_file_name is not None:
            ret = "%s.a" % module_file_name
        elif module_name is not None:
            ret = "lib%s.a" % module_name

        src_mk_obj.close()

        return ret

    def do_generate(self):
        lib_file_name = self.get_lib_file_name()
        if lib_file_name is None:
            raise Exception("The mk file %s not specify module name.")

        src_mk_obj = open(self.src_mk_path)

        # open the dst file
        tmp_file = "%s-tmp" % self.src_mk_path
        use_tmp_file = False
        if self.dst_mk_path == self.src_mk_path:
            use_tmp_file = True
            dst_mk_obj = open(tmp_file, "w")
        else:
            dst_mk_obj = open(self.dst_mk_path, "w")

        relative_path = os.path.relpath(self.lib_file_path, os.path.dirname(self.dst_mk_path))
        relative_path = "%s/$(TARGET_ARCH_ABI)/%s" % (relative_path, lib_file_name)

        # read the src file
        src_file_begin_flag = False
        for line in src_mk_obj.readlines():
            trim_line = line.lstrip(" ")
            if re.match(MKGenerator.INCLUDE_CFG_PATTERN, trim_line):
                dst_mk_obj.write("include $(PREBUILT_STATIC_LIBRARY)\n")
            elif re.match(MKGenerator.SRC_FILE_CFG_PATTERN, trim_line):
                dst_mk_obj.write("LOCAL_SRC_FILES := %s\n" % relative_path)
                if line.endswith("\\\n"):
                    src_file_begin_flag = True
            elif src_file_begin_flag:
                if not line.endswith("\\\n"):
                    src_file_begin_flag = False
            else:
                dst_mk_obj.write(line)

        #close files
        dst_mk_obj.close()
        src_mk_obj.close()

        # rename the file if temp file used
        if use_tmp_file:
            os.remove(self.src_mk_path)
            os.rename(tmp_file, self.dst_mk_path)

if __name__ == "__main__":
    parser = ArgumentParser(description="Generate prebuilt engine for Cocos Engine.")
    parser.add_argument('-s', '--src-mk', dest='src_mk', help='The source Android.mk path.')
    parser.add_argument('-d', "--dst-mk", dest='dst_mk', help='The output path of Android.mk. Default is beside the source mk with name \"Android-prebuilt.mk\".')
    parser.add_argument('-l', "--lib-path", dest='lib_path', help='The lib file path.')
    (args, unknown) = parser.parse_known_args()

    gen_obj = MKGenerator(args.src_mk, args.lib_path, args.dst_mk)
    gen_obj.do_generate()
