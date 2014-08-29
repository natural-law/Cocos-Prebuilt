#!/bin/bash

INSATLL_DIR="/Applications/cocos"
chmod -R a=rwx "${INSATLL_DIR}"

MONO_PKG="${INSATLL_DIR}/MonoFramework.pkg"
if [ -f ${MONO_PKG} ]; then
    sudo installer -pkg $MONO_PKG -target /
    rm -rf ${MONO_PKG}
fi

open "${INSATLL_DIR}"
