LOCAL_PATH := $(call my-dir)

$(call import-add-path,$(LOCAL_PATH)/../)

include $(CLEAR_VARS)

LOCAL_MODULE := cocos2dlua_shared

LOCAL_MODULE_FILENAME := libcocos2dlua

LOCAL_SRC_FILES := lua/main.cpp \
                   lua/Runtime_android.cpp \
                   ../../Classes/VisibleRect.cpp \
                   ../../Classes/AppDelegate.cpp \
                   ../../Classes/ConfigParser.cpp \
                   ../../Classes/Runtime.cpp \
                   ../../Classes/anysdkbindings.cpp \
                   ../../Classes/anysdk_manual_bindings.cpp


LOCAL_C_INCLUDES := $(LOCAL_PATH)/../../Classes

LOCAL_STATIC_LIBRARIES := curl_static_prebuilt

LOCAL_WHOLE_STATIC_LIBRARIES := cocos_lua_static
LOCAL_WHOLE_STATIC_LIBRARIES += PluginProtocolStatic

include $(BUILD_SHARED_LIBRARY)

$(call import-module,scripting/lua-bindings)
$(call import-module,anysdk/android)
