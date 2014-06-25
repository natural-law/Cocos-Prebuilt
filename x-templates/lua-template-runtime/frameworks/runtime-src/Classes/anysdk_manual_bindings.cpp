#include "anysdkbindings.hpp"
#include "AgentManager.h"
#include "ProtocolUser.h"
#include "PluginFactory.h"
#include "PluginManager.h"
#include "PluginParam.h"
#include "PluginProtocol.h"
#include "ProtocolAds.h"
#include "ProtocolAnalytics.h"
#include "ProtocolIAP.h"
#include "ProtocolPush.h"
#include "ProtocolShare.h"
#include "ProtocolSocial.h"
#include "tolua_fix.h"
#include "CCLuaValue.h"
#include "CCLuaEngine.h"
#include "LuaBasicConversions.h"

using namespace anysdk::framework;

static int tolua_anysdk_protocol_callFuncWithParam(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::PluginProtocol* cobj = nullptr;
    bool ok  = true;

#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif

#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.PluginProtocol",0,&tolua_err)) goto tolua_lerror;
#endif
    cobj = (PluginProtocol*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'tolua_anysdk_protocol_callFuncWithParam'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 1)
    {
        const char* arg0;
        std::string arg0_tmp; 
        ok &= luaval_to_std_string(tolua_S, 2, &arg0_tmp); 
        arg0 = arg0_tmp.c_str();
        if(!ok)
            return 0;
        cobj->callFuncWithParam(arg0, NULL);
        return 0;
    }
    if (argc >= 2)
    {
        const char* arg0;
        std::string arg0_tmp; 
        ok &= luaval_to_std_string(tolua_S, 2, &arg0_tmp); 
        arg0 = arg0_tmp.c_str();

        std::vector<PluginParam*> params;
 #if COCOS2D_DEBUG >= 1
        if (!tolua_istable(tolua_S, 3, 0, &tolua_err))
        {
            CCLOG("is not usertable");

            for (int i = 2; i <= argc; ++i)
            {
                auto param = (PluginParam*)tolua_tousertype(tolua_S,i+1,0);
                CCLOG("param:%s.", param->getStringValue());
                params.push_back(param);
            }
        }
        else
        {
            size_t len = lua_objlen(tolua_S, 3);
            CCLOG("is usertable: %d.", len);
            for (int i = 0; i < len; i++)
            {
                lua_pushnumber(tolua_S, i + 1);
                lua_gettable(tolua_S, 3);
                
                if (lua_isnil(tolua_S, -1) || !lua_isuserdata(tolua_S, -1))
                {
                    lua_pop(tolua_S, 1);
                    continue;
                }

                PluginParam* param = static_cast<PluginParam*>(tolua_tousertype(tolua_S, -1, NULL) );
                if (NULL != param)
                {
                    CCLOG("param: %s", param->getStringValue());
                    params.push_back(param);
                }
                lua_pop(tolua_S, 1);
            }
        }
#endif
        cobj->callFuncWithParam(arg0, params);
        return 0;
    }

    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "callFuncWithParam",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'tolua_anysdk_protocol_callFuncWithParam'.",&tolua_err);
#endif

    return 0;
}

static void extend_PluginProtocol(lua_State* tolua_S)
{
    lua_pushstring(tolua_S,"anysdk.PluginProtocol");
    lua_rawget(tolua_S,LUA_REGISTRYINDEX);
    if (lua_istable(tolua_S,-1))
    {
        tolua_function(tolua_S, "callFuncWithParam", tolua_anysdk_protocol_callFuncWithParam);
    }
    lua_pop(tolua_S, 1);
}

static int tolua_anysdk_ProtocolPush_setTags(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::ProtocolPush* cobj = nullptr;
    bool ok  = true;

#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif

#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.ProtocolPush",0,&tolua_err)) goto tolua_lerror;
#endif
    cobj = (ProtocolPush*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'tolua_anysdk_ProtocolPush_setTags'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 1)
    {
#if COCOS2D_DEBUG >= 1
        if( tolua_istable(tolua_S, 2, 0, &tolua_err) )
        {
            size_t len = lua_objlen(tolua_S, 2);
            CCLOG("is usertable, len: %d.", len);
            std::list<std::string> tags;
            for (int i = 0; i < len; i++)
            {
                lua_pushnumber(tolua_S, i + 1);
                lua_gettable(tolua_S, 2);
                
                if (lua_isnil(tolua_S, -1) || !lua_isuserdata(tolua_S, -1))
                {
                    lua_pop(tolua_S, 1);
                    continue;
                }

                std::string param = (std::string)tolua_tostring(tolua_S, 2, 0);
                if (param.length())
                {
                    CCLOG("param: %s", param.c_str());
                    tags.push_back(param);
                }
                lua_pop(tolua_S, 1);
            }
            cobj->setTags(tags);
        }
        else{
            CCLOG("%s has wrong type of arguments.", "setTags");
        }
#endif
        return 0;
    }

    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "setTags",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'tolua_anysdk_ProtocolPush_setTags'.",&tolua_err);
#endif

    return 0;
}

static int tolua_anysdk_ProtocolPush_delTags(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::ProtocolPush* cobj = nullptr;
    bool ok  = true;

#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif

#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.ProtocolPush",0,&tolua_err)) goto tolua_lerror;
#endif
    cobj = (ProtocolPush*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'tolua_anysdk_ProtocolPush_delTags'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 1)
    {
#if COCOS2D_DEBUG >= 1
        if( tolua_istable(tolua_S, 2, 0, &tolua_err) )
        {
            size_t len = lua_objlen(tolua_S, 2);
            CCLOG("is usertable, len: %d.", len);
            std::list<std::string> tags;
            for (int i = 0; i < len; i++)
            {
                lua_pushnumber(tolua_S, i + 1);
                lua_gettable(tolua_S, 2);
                
                if (lua_isnil(tolua_S, -1) || !lua_isuserdata(tolua_S, -1))
                {
                    lua_pop(tolua_S, 1);
                    continue;
                }

                std::string param = (std::string)tolua_tostring(tolua_S, 2, 0);
                if (param.length())
                {
                    CCLOG("param: %s", param.c_str());
                    tags.push_back(param);
                }
                lua_pop(tolua_S, 1);
            }
            cobj->delTags(tags);
        }
        else{
            CCLOG("%s has wrong type of arguments.", "delTags");
        }
#endif
        return 0;
    }

    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "delTags",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'tolua_anysdk_ProtocolPush_delTags'.",&tolua_err);
#endif

    return 0;
}

static void extend_ProtocolPush(lua_State* tolua_S)
{
    lua_pushstring(tolua_S,"anysdk.ProtocolPush");
    lua_rawget(tolua_S,LUA_REGISTRYINDEX);
    if (lua_istable(tolua_S,-1))
    {
        tolua_function(tolua_S, "setTags", tolua_anysdk_ProtocolPush_setTags);
        tolua_function(tolua_S, "delTags", tolua_anysdk_ProtocolPush_delTags);
        //tolua_function(tolua_S, "setActionListener", tolua_anysdk_ProtocolPush_setActionListener);
    }
    lua_pop(tolua_S, 1);
}

class ProtocolIAPResultListener : public PayResultListener
{
public:
    ProtocolIAPResultListener():_handler(0)
    {
    }
    ~ProtocolIAPResultListener()
    {
        LuaStack* stack = LuaEngine::getInstance()->getLuaStack();
        stack->removeScriptHandler(_handler);
    }

    virtual void onPayResult(PayResultCode ret, const char* msg, TProductInfo info)
    {
        CCLOG("on pay result: %d, msg: %s.", ret, msg);
        LuaStack* stack = LuaEngine::getInstance()->getLuaStack();
        lua_State* tolua_S    = stack->getLuaState();
        tolua_pushnumber(tolua_S, (lua_Number)ret);
        tolua_pushstring(tolua_S, (const char *)msg);
        lua_newtable(tolua_S);
        if (nullptr != tolua_S)
        {
            for (auto iter = info.begin(); iter != info.end(); ++iter)
            {
                std::string key = iter->first;
                std::string value = iter->second;
                lua_pushstring(tolua_S, key.c_str());
                lua_pushstring(tolua_S, value.c_str());
                lua_rawset(tolua_S, -3);
            }
        }
        stack->executeFunctionByHandler(_handler, 3);
        stack->clean();
        //remove

    }

    void setHandler(LUA_FUNCTION handler)
    {
        _handler = handler;
        CCLOG("_handler: %d.", (int)_handler);
    }
private:
    LUA_FUNCTION _handler;
};

static int tolua_anysdk_ProtocolIAP_setResultListener(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::ProtocolIAP* cobj = nullptr;
    bool ok  = true;
    CCLOG("on setResultListener.");
#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif

#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.ProtocolIAP",0,&tolua_err)) goto tolua_lerror;
#endif
    cobj = (ProtocolIAP*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'tolua_anysdk_ProtocolIAP_setResultListener'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    CCLOG("in set listener, argc: %d.", argc);
    if (argc == 1)
    {
#if COCOS2D_DEBUG >= 1
        if (!toluafix_isfunction(tolua_S,2,"LUA_FUNCTION",0,&tolua_err) )
        {
            goto tolua_lerror;
        }
#endif
        LUA_FUNCTION handler = (  toluafix_ref_function(tolua_S,2,0));

        CCLOG("will set listener:");
        ProtocolIAPResultListener* listener = new ProtocolIAPResultListener();
        listener->setHandler(handler);
        cobj->setResultListener(listener);

        CCLOG("set listener end");

        return 0;
    }

    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "setResultListener",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'tolua_anysdk_ProtocolIAP_setResultListener'.",&tolua_err);
#endif

    return 0;
}

static int tolua_anysdk_ProtocolIAP_payForProduct(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::ProtocolIAP* cobj = nullptr;
    bool ok  = true;
    CCLOG("on payForProduct.");
#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif

#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.ProtocolIAP",0,&tolua_err)) goto tolua_lerror;
#endif
    cobj = (ProtocolIAP*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'tolua_anysdk_ProtocolIAP_payForProduct'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    CCLOG("in pay product, argc: %d.", argc);
    if (argc == 1)
    {
#if COCOS2D_DEBUG >= 1
        if (tolua_istable(tolua_S, 2, 0, &tolua_err))
        {
            CCLOG("is table");
            TProductInfo strmap;
            lua_pushnil(tolua_S);                                            /* first key L: lotable ..... nil */
            while ( 0 != lua_next(tolua_S, 2 ) )                             /* L: lotable ..... key value */
            {
                if (!lua_isstring(tolua_S, -2))
                {
                    lua_pop(tolua_S, 1);                                      /* removes 'value'; keep 'key' for next iteration*/
                    continue;
                }
                if (lua_isnil(tolua_S, -1) || !lua_isstring(tolua_S, -1))
                {
                    lua_pop(tolua_S, 1);
                    continue;
                }
                std::string key = "";
                luaval_to_std_string(tolua_S, -2, &key);
                std::string value = "";
                luaval_to_std_string(tolua_S, -1, &value);
                CCLOG("key: %s, value: %s.", key.c_str(), value.c_str());
                strmap.insert( StringMap::value_type(key, value) );
                lua_pop(tolua_S, 1);                                          /* L: lotable ..... key */
            }
            cobj->payForProduct(strmap);
            CCLOG("end");
        }
#endif
        return 0;
    }

    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "payForProduct",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'tolua_anysdk_ProtocolIAP_payForProduct'.",&tolua_err);
#endif

    return 0;
}

static void extend_ProtocolIAP(lua_State* tolua_S)
{
    lua_pushstring(tolua_S,"anysdk.ProtocolIAP");
    lua_rawget(tolua_S,LUA_REGISTRYINDEX);
    if (lua_istable(tolua_S,-1))
    {
        tolua_function(tolua_S, "setResultListener", tolua_anysdk_ProtocolIAP_setResultListener);
        tolua_function(tolua_S, "payForProduct", tolua_anysdk_ProtocolIAP_payForProduct);
    }
    lua_pop(tolua_S, 1);
}

class ProtocolAdsListener : public AdsListener
{
public:
    ProtocolAdsListener():_handler(0)
    {
    }
    ~ProtocolAdsListener()
    {
        LuaStack* stack = LuaEngine::getInstance()->getLuaStack();
        stack->removeScriptHandler(_handler);
    }

    virtual void onAdsResult(AdsResultCode code, const char* msg)
    {
        CCLOG("on pay result: %d, msg: %s.", code, msg);
        LuaStack* stack = LuaEngine::getInstance()->getLuaStack();
        lua_State* tolua_S    = stack->getLuaState();
        tolua_pushnumber(tolua_S, (lua_Number)code);
        tolua_pushstring(tolua_S, (const char *)msg);
        stack->executeFunctionByHandler(_handler, 2);
        stack->clean();
    }
    virtual void onPlayerGetPoints(ProtocolAds* pAdsPlugin, int points)
    {
        CCLOG("onPlayerGetPoints. points: %d.", points);
        LuaStack* stack = LuaEngine::getInstance()->getLuaStack();
        lua_State* tolua_S    = stack->getLuaState();
        object_to_luaval<ProtocolAds>(tolua_S, "anysdk.ProtocolAds",(ProtocolAds*)pAdsPlugin);
        tolua_pushnumber(tolua_S, (lua_Number)points);
        stack->executeFunctionByHandler(_handler, 2);
        stack->clean();
    }

    void setHandler(LUA_FUNCTION handler)
    {
        _handler = handler;
        CCLOG("_handler: %d.", (int)_handler);
    }
private:
    LUA_FUNCTION _handler;
};

static int tolua_anysdk_ProtocolAds_setAdsListener(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::ProtocolAds* cobj = nullptr;
    bool ok  = true;
    CCLOG("on setAdsListener.");
#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif

#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.ProtocolAds",0,&tolua_err)) goto tolua_lerror;
#endif
    cobj = (ProtocolAds*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'tolua_anysdk_ProtocolAds_setAdsListener'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    CCLOG("in set listener, argc: %d.", argc);
    if (argc == 1)
    {
#if COCOS2D_DEBUG >= 1
        if (!toluafix_isfunction(tolua_S,2,"LUA_FUNCTION",0,&tolua_err) )
        {
            goto tolua_lerror;
        }
#endif
        LUA_FUNCTION handler = (  toluafix_ref_function(tolua_S,2,0));

        CCLOG("will set ads listener:");
        ProtocolAdsListener* listener = new ProtocolAdsListener();
        listener->setHandler(handler);
        cobj->setAdsListener(listener);

        CCLOG("set listener end");

        return 0;
    }

    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "setAdsListener",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'tolua_anysdk_ProtocolAds_setAdsListener'.",&tolua_err);
#endif

    return 0;
}

static void extend_ProtocolAds(lua_State* tolua_S)
{
    lua_pushstring(tolua_S,"anysdk.ProtocolAds");
    lua_rawget(tolua_S,LUA_REGISTRYINDEX);
    if (lua_istable(tolua_S,-1))
    {
        tolua_function(tolua_S, "setAdsListener", tolua_anysdk_ProtocolAds_setAdsListener);
    }
    lua_pop(tolua_S, 1);
}

class ProtocolSocialListener : public SocialListener
{
public:
    ProtocolSocialListener():_handler(0)
    {
    }
    ~ProtocolSocialListener()
    {
        LuaStack* stack = LuaEngine::getInstance()->getLuaStack();
        stack->removeScriptHandler(_handler);
    }

    virtual void onSocialResult(SocialRetCode code, const char* msg)
    {
        CCLOG("on social result: %d, msg: %s.", code, msg);
        LuaStack* stack = LuaEngine::getInstance()->getLuaStack();
        lua_State* tolua_S    = stack->getLuaState();
        tolua_pushnumber(tolua_S, (lua_Number)code);
        tolua_pushstring(tolua_S, (const char *)msg);
        stack->executeFunctionByHandler(_handler, 2);
        stack->clean();
    }

    void setHandler(LUA_FUNCTION handler)
    {
        _handler = handler;
        CCLOG("_handler: %d.", (int)_handler);
    }
private:
    LUA_FUNCTION _handler;
};

static int tolua_anysdk_ProtocolSocial_setListener(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::ProtocolSocial* cobj = nullptr;
    bool ok  = true;
    CCLOG("on social setListener.");
#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif

#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.ProtocolSocial",0,&tolua_err)) goto tolua_lerror;
#endif
    cobj = (ProtocolSocial*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'tolua_anysdk_ProtocolSocial_setListener'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    CCLOG("in set listener, argc: %d.", argc);
    if (argc == 1)
    {
#if COCOS2D_DEBUG >= 1
        if (!toluafix_isfunction(tolua_S,2,"LUA_FUNCTION",0,&tolua_err) )
        {
            goto tolua_lerror;
        }
#endif
        LUA_FUNCTION handler = (  toluafix_ref_function(tolua_S,2,0));

        CCLOG("will set ads listener:");
        ProtocolSocialListener* listener = new ProtocolSocialListener();
        listener->setHandler(handler);
        cobj->setListener(listener);

        CCLOG("set listener end");

        return 0;
    }

    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "setListener",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'tolua_anysdk_ProtocolSocial_setListener'.",&tolua_err);
#endif

    return 0;
}

static int tolua_anysdk_ProtocolSocial_unlockAchievement(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::ProtocolSocial* cobj = nullptr;
    bool ok  = true;
    CCLOG("on social unlockAchievement.");
#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif

#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.ProtocolSocial",0,&tolua_err)) goto tolua_lerror;
#endif
    cobj = (ProtocolSocial*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'tolua_anysdk_ProtocolSocial_unlockAchievement'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    CCLOG("in set unlockAchievement, argc: %d.", argc);
    if (argc == 1)
    {
#if COCOS2D_DEBUG >= 1
        if (tolua_istable(tolua_S, 2, 0, &tolua_err))
        {
            CCLOG("is table");
            TAchievementInfo strmap;
            lua_pushnil(tolua_S);                                            /* first key L: lotable ..... nil */
            while ( 0 != lua_next(tolua_S, 2 ) )                             /* L: lotable ..... key value */
            {
                if (!lua_isstring(tolua_S, -2))
                {
                    lua_pop(tolua_S, 1);                                      /* removes 'value'; keep 'key' for next iteration*/
                    continue;
                }
                if (lua_isnil(tolua_S, -1) || !lua_isstring(tolua_S, -1))
                {
                    lua_pop(tolua_S, 1);
                    continue;
                }
                std::string key = "";
                luaval_to_std_string(tolua_S, -2, &key);
                std::string value = "";
                luaval_to_std_string(tolua_S, -1, &value);
                strmap.insert( StringMap::value_type(key, value) );
                lua_pop(tolua_S, 1);                                          /* L: lotable ..... key */
            }
            cobj->unlockAchievement(strmap);

            CCLOG("set unlockAchievement end");
        }
#endif

        return 0;
    }

    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "unlockAchievement",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'tolua_anysdk_ProtocolSocial_unlockAchievement'.",&tolua_err);
#endif

    return 0;
}

static void extend_ProtocolSocial(lua_State* tolua_S)
{
    lua_pushstring(tolua_S,"anysdk.ProtocolSocial");
    lua_rawget(tolua_S,LUA_REGISTRYINDEX);
    if (lua_istable(tolua_S,-1))
    {
        tolua_function(tolua_S, "setListener", tolua_anysdk_ProtocolSocial_setListener);
        tolua_function(tolua_S, "unlockAchievement", tolua_anysdk_ProtocolSocial_unlockAchievement);
    }
    lua_pop(tolua_S, 1);
}

int tolua_anysdk_ProtocolAnalytics_logEvent(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::ProtocolAnalytics* cobj = nullptr;
    bool ok  = true;

#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif


#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.ProtocolAnalytics",0,&tolua_err)) goto tolua_lerror;
#endif

    cobj = (anysdk::framework::ProtocolAnalytics*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'tolua_anysdk_ProtocolAnalytics_logEvent'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 1) 
    {
        const char* arg0;

        std::string arg0_tmp; ok &= luaval_to_std_string(tolua_S, 2, &arg0_tmp); arg0 = arg0_tmp.c_str();
        if(!ok)
            return 0;
        cobj->logEvent(arg0);
        return 0;
    }
    if (argc == 2) 
    {
        const char* arg0;
        std::string arg0_tmp; ok &= luaval_to_std_string(tolua_S, 2, &arg0_tmp); arg0 = arg0_tmp.c_str();

        if(!ok)
            return 0;
#if COCOS2D_DEBUG >= 1
        if (tolua_istable(tolua_S, 3, 0, &tolua_err))
        {
            CCLOG("is table");
            LogEventParamMap* strmap;
            lua_pushnil(tolua_S);                                            /* first key L: lotable ..... nil */
            while ( 0 != lua_next(tolua_S, 3 ) )                             /* L: lotable ..... key value */
            {
                if (!lua_isstring(tolua_S, -2))
                {
                    lua_pop(tolua_S, 1);                                      /* removes 'value'; keep 'key' for next iteration*/
                    continue;
                }
                if (lua_isnil(tolua_S, -1) || !lua_isstring(tolua_S, -1))
                {
                    lua_pop(tolua_S, 1);
                    continue;
                }
                std::string key = "";
                luaval_to_std_string(tolua_S, -2, &key);
                std::string value = "";
                luaval_to_std_string(tolua_S, -1, &value);
                CCLOG("key: %s, value: %s.", key.c_str(), value.c_str());
                strmap->insert( StringMap::value_type(key, value) );
                lua_pop(tolua_S, 1);                                          /* L: lotable ..... key */
            }
            cobj->logEvent(arg0, strmap);
        }
#endif
        return 0;
    }
    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "logEvent",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'tolua_anysdk_ProtocolAnalytics_logEvent'.",&tolua_err);
#endif

    return 0;
}

static void extend_ProtocolAnalytics(lua_State* tolua_S)
{
    lua_pushstring(tolua_S,"anysdk.ProtocolAnalytics");
    lua_rawget(tolua_S,LUA_REGISTRYINDEX);
    if (lua_istable(tolua_S,-1))
    {
        tolua_function(tolua_S, "logEvent", tolua_anysdk_ProtocolAnalytics_logEvent);
    }
    lua_pop(tolua_S, 1);
}

class ProtocolUserActionListener : public UserActionListener
{
public:
    ProtocolUserActionListener():_handler(0)
    {
    }
    ~ProtocolUserActionListener()
    {
        LuaStack* stack = LuaEngine::getInstance()->getLuaStack();
        stack->removeScriptHandler(_handler);
    }

    virtual void onActionResult(ProtocolUser* pPlugin, UserActionResultCode code, const char* msg)
    {
        CCLOG("on action result: %d, msg: %s.", code, msg);
        LuaStack* stack = LuaEngine::getInstance()->getLuaStack();
        lua_State* tolua_S    = stack->getLuaState();
        object_to_luaval<ProtocolUser>(tolua_S, "anysdk.ProtocolUser",(ProtocolUser*)pPlugin);
        tolua_pushnumber(tolua_S, (lua_Number)code);
        tolua_pushstring(tolua_S, (const char *)msg);
        stack->executeFunctionByHandler(_handler, 3);
        stack->clean();
    }

    void setHandler(LUA_FUNCTION handler)
    {
        _handler = handler;
        CCLOG("_handler: %d.", (int)_handler);
    }
private:
    LUA_FUNCTION _handler;
};

static int tolua_anysdk_ProtocolUser_setActionListener(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::ProtocolUser* cobj = nullptr;
    bool ok  = true;
    CCLOG("on setActionListener.");
#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif

#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.ProtocolUser",0,&tolua_err)) goto tolua_lerror;
#endif
    cobj = (ProtocolUser*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'tolua_anysdk_ProtocolUser_setActionListener'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    CCLOG("in set listener, argc: %d.", argc);
    if (argc == 1)
    {
#if COCOS2D_DEBUG >= 1
        if (!toluafix_isfunction(tolua_S,2,"LUA_FUNCTION",0,&tolua_err) )
        {
            goto tolua_lerror;
        }
#endif
        LUA_FUNCTION handler = (  toluafix_ref_function(tolua_S,2,0));

        CCLOG("will set listener:");
        ProtocolUserActionListener* listener = new ProtocolUserActionListener();
        listener->setHandler(handler);
        cobj->setActionListener(listener);

        CCLOG("set listener end");

        return 0;
    }

    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "setActionListener",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'tolua_anysdk_ProtocolUser_setActionListener'.",&tolua_err);
#endif

    return 0;
}

static void extend_ProtocolUser(lua_State* tolua_S)
{
    lua_pushstring(tolua_S,"anysdk.ProtocolUser");
    lua_rawget(tolua_S,LUA_REGISTRYINDEX);
    if (lua_istable(tolua_S,-1))
    {
        tolua_function(tolua_S, "setActionListener", tolua_anysdk_ProtocolUser_setActionListener);
    }
    lua_pop(tolua_S, 1);
}

static int tolua_anysdk_AgentManager_getIAPPlugin(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::AgentManager* cobj = nullptr;
    bool ok  = true;
#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif

#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.AgentManager",0,&tolua_err)) goto tolua_lerror;
#endif
    cobj = (AgentManager*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'tolua_anysdk_AgentManager_getIAPPlugin'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 0)
    {
        if(!ok)
            return 0;
        std::map<std::string , ProtocolIAP*>* iap_plugins = cobj->getIAPPlugin();

        if (nullptr == iap_plugins)
        {
            lua_pushnil(tolua_S);
        }
        else
        {
            lua_newtable(tolua_S);
            if (nullptr != tolua_S)
            {
                for (auto iter = iap_plugins->begin(); iter != iap_plugins->end(); ++iter)
                {
                    std::string key = iter->first;
                    ProtocolIAP* value = iter->second;
                    lua_pushstring(tolua_S, key.c_str());
                    object_to_luaval<ProtocolIAP>(tolua_S, "anysdk.ProtocolIAP",(ProtocolIAP*)value);
                    lua_rawset(tolua_S, -3);
                }
            }
        }
        return 1;
    }

    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "getIAPPlugin",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'tolua_anysdk_AgentManager_getIAPPlugin'.",&tolua_err);
#endif

    return 0;
}

static void extend_AgentManager(lua_State* tolua_S)
{
    lua_pushstring(tolua_S,"anysdk.AgentManager");
    lua_rawget(tolua_S,LUA_REGISTRYINDEX);
    if (lua_istable(tolua_S,-1))
    {
        tolua_function(tolua_S, "getIAPPlugin", tolua_anysdk_AgentManager_getIAPPlugin);
    }
    lua_pop(tolua_S, 1);
}

int lua_anysdkbindings_PluginParam_PluginParam(lua_State* tolua_S)
{
    int argc = 0;
    PluginParam* cobj = nullptr;
    bool ok  = true;

#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif


#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertable(tolua_S,1,"anysdk.PluginParam",0,&tolua_err)) goto tolua_lerror;
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 1) 
    {
        if(!ok)
            return 0;
#if COCOS2D_DEBUG >= 1
        if(tolua_isboolean(tolua_S, 2, 0, &tolua_err))
        {
            bool arg1 = (bool)tolua_toboolean(tolua_S, 2, 0);
            cobj = new PluginParam((bool)arg1);
        }
        else if (tolua_isnumber(tolua_S, 2, 0, &tolua_err))
        {
            double arg1 = (double)tolua_tonumber(tolua_S, 2, 0);
            float argf = (float)arg1;
            int argi = (int)arg1;
            float temp = argf - (float)argi;

            if ( temp > 0.000001){
                cobj = new PluginParam((float)argf);
            }
            else{
                cobj = new PluginParam((int)argi);
            }
        }
        else if (tolua_isstring(tolua_S, 2, 0, &tolua_err))
        {
            std::string arg1 = (std::string)tolua_tostring(tolua_S, 2, 0);
            const char* temp = arg1.c_str();
            cobj = new PluginParam(temp);
        }
        else if (tolua_istable(tolua_S, 2, 0, &tolua_err))
        {
            CCLOG("is table");
            typedef std::map<std::string, std::string> StringMap;
            StringMap strmap;
            lua_pushnil(tolua_S);                                            /* first key L: lotable ..... nil */
            while ( 0 != lua_next(tolua_S, 2 ) )                             /* L: lotable ..... key value */
            {
                if (!lua_isstring(tolua_S, -2))
                {
                    lua_pop(tolua_S, 1);                                      /* removes 'value'; keep 'key' for next iteration*/
                    continue;
                }
                if (lua_isnil(tolua_S, -1) || !lua_isstring(tolua_S, -1))
                {
                    lua_pop(tolua_S, 1);
                    continue;
                }
                std::string key = "";
                luaval_to_std_string(tolua_S, -2, &key);
                std::string value = "";
                luaval_to_std_string(tolua_S, -1, &value);
                strmap.insert( StringMap::value_type(key, value) );
                lua_pop(tolua_S, 1);                                          /* L: lotable ..... key */
            }
            cobj = new PluginParam(strmap);
            CCLOG("end");
        }
#endif

        if(nullptr != cobj)
        {
            tolua_pushusertype(tolua_S,(void*)cobj,"anysdk.PluginParam");
            tolua_register_gc(tolua_S,lua_gettop(tolua_S));
        }
        else
        {
            lua_pushnil(tolua_S);
        }

        return 1;
    }
    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "PluginParam",argc, 0);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'lua_anysdkbindings_PluginParam_PluginParam'.",&tolua_err);
#endif

    return 0;
}

int lua_anysdkbindings_PluginParam_getCurrentType(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::PluginParam* cobj = nullptr;
    bool ok  = true;

#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif


#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.PluginParam",0,&tolua_err)) goto tolua_lerror;
#endif

    cobj = (anysdk::framework::PluginParam*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'lua_anysdkbindings_PluginParam_getCurrentType'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 0) 
    {
        if(!ok)
            return 0;

        int value = cobj->getCurrentType();
        tolua_pushnumber(tolua_S, (lua_Number)value);
        return 1;
    }
    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "getCurrentType",argc, 0);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'lua_anysdkbindings_PluginParam_getCurrentType'.",&tolua_err);
#endif

    return 0;
}

int lua_anysdkbindings_PluginParam_getIntValue(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::PluginParam* cobj = nullptr;
    bool ok  = true;

#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif


#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.PluginParam",0,&tolua_err)) goto tolua_lerror;
#endif

    cobj = (anysdk::framework::PluginParam*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'lua_anysdkbindings_PluginParam_getIntValue'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 0) 
    {
        if(!ok)
            return 0;

        int value = cobj->getIntValue();
        CCLOG("get int value:%d", value);
        tolua_pushnumber(tolua_S, (lua_Number)value);
        return 1;
    }
    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "getIntValue",argc, 0);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'lua_anysdkbindings_PluginParam_getIntValue'.",&tolua_err);
#endif

    return 0;
}

int lua_anysdkbindings_PluginParam_getFloatValue(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::PluginParam* cobj = nullptr;
    bool ok  = true;

#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif


#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.PluginParam",0,&tolua_err)) goto tolua_lerror;
#endif

    cobj = (anysdk::framework::PluginParam*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'lua_anysdkbindings_PluginParam_getFloatValue'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 0) 
    {
        if(!ok)
            return 0;

        float value = cobj->getFloatValue();
        CCLOG("get float value:%f.", value);
        tolua_pushnumber(tolua_S, (lua_Number)value);
        return 1;
    }
    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "getFloatValue",argc, 0);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'lua_anysdkbindings_PluginParam_getFloatValue'.",&tolua_err);
#endif

    return 0;
}

int lua_anysdkbindings_PluginParam_getStringValue(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::PluginParam* cobj = nullptr;
    bool ok  = true;

#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif


#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.PluginParam",0,&tolua_err)) goto tolua_lerror;
#endif

    cobj = (anysdk::framework::PluginParam*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'lua_anysdkbindings_PluginParam_getStringValue'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 0) 
    {
        if(!ok)
            return 0;

        const char* value = cobj->getStringValue();
        tolua_pushstring(tolua_S, (const char*)value);
        return 1;
    }
    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "getStringValue",argc, 0);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'lua_anysdkbindings_PluginParam_getStringValue'.",&tolua_err);
#endif

    return 0;
}

int lua_anysdkbindings_PluginParam_getBoolValue(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::PluginParam* cobj = nullptr;
    bool ok  = true;

#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif


#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.PluginParam",0,&tolua_err)) goto tolua_lerror;
#endif

    cobj = (anysdk::framework::PluginParam*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'lua_anysdkbindings_PluginParam_getBoolValue'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 0) 
    {
        if(!ok)
            return 0;

        bool value = cobj->getBoolValue();
        CCLOG("get bool value:%d.", value);
        tolua_pushboolean(tolua_S, (bool)value);
        return 1;
    }
    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "getBoolValue",argc, 0);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'lua_anysdkbindings_PluginParam_getBoolValue'.",&tolua_err);
#endif

    return 0;
}

int lua_anysdkbindings_PluginParam_getStrMapValue(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::PluginParam* cobj = nullptr;
    bool ok  = true;

#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif


#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.PluginParam",0,&tolua_err)) goto tolua_lerror;
#endif

    cobj = (anysdk::framework::PluginParam*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'lua_anysdkbindings_PluginParam_getStrMapValue'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 0) 
    {
        if(!ok)
            return 0;
        typedef std::map<std::string, std::string> StringMap;
        StringMap strmap = cobj->getStrMapValue();
        lua_newtable(tolua_S);
        if (nullptr != tolua_S)
        {
            for (auto iter = strmap.begin(); iter != strmap.end(); ++iter)
            {
                std::string key = iter->first;
                std::string value = iter->second;
                lua_pushstring(tolua_S, key.c_str());
                lua_pushstring(tolua_S, value.c_str());
                lua_rawset(tolua_S, -3);
            }
        }
        return 1;
    }
    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "getStrMapValue",argc, 0);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'lua_anysdkbindings_PluginParam_getStrMapValue'.",&tolua_err);
#endif

    return 0;
}

int lua_register_anysdkbindings_PluginParam(lua_State* tolua_S)
{
    tolua_usertype(tolua_S,"anysdk.PluginParam");
    tolua_cclass(tolua_S,"PluginParam","anysdk.PluginParam","anysdk.PluginParam",nullptr);

    tolua_beginmodule(tolua_S,"PluginParam");
        tolua_function(tolua_S,"PluginParam",lua_anysdkbindings_PluginParam_PluginParam);
        tolua_function(tolua_S,"getCurrentType",lua_anysdkbindings_PluginParam_getCurrentType);
        tolua_function(tolua_S,"getIntValue",lua_anysdkbindings_PluginParam_getIntValue);
        tolua_function(tolua_S,"getFloatValue",lua_anysdkbindings_PluginParam_getFloatValue);
        tolua_function(tolua_S,"getBoolValue",lua_anysdkbindings_PluginParam_getBoolValue);
        tolua_function(tolua_S,"getStringValue",lua_anysdkbindings_PluginParam_getStringValue);
        tolua_function(tolua_S,"getStrMapValue",lua_anysdkbindings_PluginParam_getStrMapValue);
    tolua_endmodule(tolua_S);
    std::string typeName = typeid(anysdk::framework::PluginParam).name();
    g_luaType[typeName] = "anysdk.PluginParam";
    g_typeCast["PluginParam"] = "anysdk.PluginParam";
    return 1;
}

class ProtocolShareListener : public ShareResultListener
{
public:
    ProtocolShareListener():_handler(0)
    {
    }
    ~ProtocolShareListener()
    {
        LuaStack* stack = LuaEngine::getInstance()->getLuaStack();
        stack->removeScriptHandler(_handler);
    }

    virtual void onShareResult(ShareResultCode ret, const char* msg)
    {
        CCLOG("on share result result: %d, msg: %s.", ret, msg);
        LuaStack* stack = LuaEngine::getInstance()->getLuaStack();
        lua_State* tolua_S    = stack->getLuaState();
        // object_to_luaval<ProtocolUser>(tolua_S, "anysdk.ProtocolUser",(ProtocolUser*)pPlugin);
        tolua_pushnumber(tolua_S, (lua_Number)ret);
        tolua_pushstring(tolua_S, (const char *)msg);
        stack->executeFunctionByHandler(_handler, 2);
        stack->clean();
    }

    void setHandler(LUA_FUNCTION handler)
    {
        _handler = handler;
        CCLOG("_handler: %d.", (int)_handler);
    }
private:
    LUA_FUNCTION _handler;
};

static int tolua_anysdk_ProtocolShare_setResultListener(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::ProtocolShare* cobj = nullptr;
    bool ok  = true;
    CCLOG("on setResultListener.");
#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif

#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.ProtocolShare",0,&tolua_err)) goto tolua_lerror;
#endif
    cobj = (ProtocolShare*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'tolua_anysdk_ProtocolShare_setResultListener'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    CCLOG("in set listener, argc: %d.", argc);
    if (argc == 1)
    {
#if COCOS2D_DEBUG >= 1
        if (!toluafix_isfunction(tolua_S,2,"LUA_FUNCTION",0,&tolua_err) )
        {
            goto tolua_lerror;
        }
#endif
        LUA_FUNCTION handler = (  toluafix_ref_function(tolua_S,2,0));

        CCLOG("will set listener:");
        ProtocolShareListener* listener = new ProtocolShareListener();
        listener->setHandler(handler);
        cobj->setResultListener(listener);

        CCLOG("set listener end");

        return 0;
    }

    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "setResultListener",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'tolua_anysdk_ProtocolShare_setResultListener'.",&tolua_err);
#endif

    return 0;
}

int lua_anysdkbindings_ProtocolShare_share(lua_State* tolua_S)
{
    int argc = 0;
    anysdk::framework::ProtocolShare* cobj = nullptr;
    bool ok  = true;

#if COCOS2D_DEBUG >= 1
    tolua_Error tolua_err;
#endif


#if COCOS2D_DEBUG >= 1
    if (!tolua_isusertype(tolua_S,1,"anysdk.ProtocolShare",0,&tolua_err)) goto tolua_lerror;
#endif

    cobj = (anysdk::framework::ProtocolShare*)tolua_tousertype(tolua_S,1,0);

#if COCOS2D_DEBUG >= 1
    if (!cobj) 
    {
        tolua_error(tolua_S,"invalid 'cobj' in function 'lua_anysdkbindings_ProtocolShare_share'", nullptr);
        return 0;
    }
#endif

    argc = lua_gettop(tolua_S)-1;
    if (argc == 1) 
    {
#if COCOS2D_DEBUG >= 1
        if (tolua_istable(tolua_S, 2, 0, &tolua_err))
        {
            CCLOG("is table");
            TShareInfo strmap;
            lua_pushnil(tolua_S);                                            /* first key L: lotable ..... nil */
            while ( 0 != lua_next(tolua_S, 2 ) )                             /* L: lotable ..... key value */
            {
                if (!lua_isstring(tolua_S, -2))
                {
                    lua_pop(tolua_S, 1);                                      /* removes 'value'; keep 'key' for next iteration*/
                    continue;
                }
                if (lua_isnil(tolua_S, -1) || !lua_isstring(tolua_S, -1))
                {
                    lua_pop(tolua_S, 1);
                    continue;
                }
                std::string key = "";
                luaval_to_std_string(tolua_S, -2, &key);
                std::string value = "";
                luaval_to_std_string(tolua_S, -1, &value);
                strmap.insert( StringMap::value_type(key, value) );
                lua_pop(tolua_S, 1);                                          /* L: lotable ..... key */
            }
            cobj->share(strmap);
            CCLOG("end");
        }
#endif
        return 0;
    }
    CCLOG("%s has wrong number of arguments: %d, was expecting %d \n", "share",argc, 1);
    return 0;

#if COCOS2D_DEBUG >= 1
    tolua_lerror:
    tolua_error(tolua_S,"#ferror in function 'lua_anysdkbindings_ProtocolShare_share'.",&tolua_err);
#endif

    return 0;
}

int lua_register_anysdkbindings_ProtocolShare(lua_State* tolua_S)
{
    tolua_usertype(tolua_S,"anysdk.ProtocolShare");
    tolua_cclass(tolua_S,"ProtocolShare","anysdk.ProtocolShare","anysdk.PluginProtocol",nullptr);

    tolua_beginmodule(tolua_S,"ProtocolShare");
        tolua_function(tolua_S,"share",lua_anysdkbindings_ProtocolShare_share);
        tolua_function(tolua_S, "setResultListener", tolua_anysdk_ProtocolShare_setResultListener);
    tolua_endmodule(tolua_S);
    std::string typeName = typeid(anysdk::framework::ProtocolShare).name();
    g_luaType[typeName] = "anysdk.ProtocolShare";
    g_typeCast["ProtocolShare"] = "anysdk.ProtocolShare";
    return 1;
}

int register_all_anysdk_manual_bindings(lua_State* tolua_S)
{
    if (NULL == tolua_S)
        return 0;

	extend_PluginProtocol(tolua_S);
	extend_ProtocolUser(tolua_S);
	extend_ProtocolIAP(tolua_S);
	extend_AgentManager(tolua_S);
	extend_ProtocolAnalytics(tolua_S);
	extend_ProtocolAds(tolua_S);
	extend_ProtocolSocial(tolua_S);
	// extend_PluginManager(tolua_S);
	extend_ProtocolPush(tolua_S);

    tolua_open(tolua_S);
    tolua_module(tolua_S,"anysdk",0);
    tolua_beginmodule(tolua_S,"anysdk");

    lua_register_anysdkbindings_PluginParam(tolua_S);
    lua_register_anysdkbindings_ProtocolShare(tolua_S);
    
    tolua_endmodule(tolua_S);

	return 1;
}

