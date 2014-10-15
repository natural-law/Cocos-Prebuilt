#!/bin/bash

# change the premission of cocos folder
INSATLL_DIR="/Applications/cocos"

# install cocos studio
MONO_PKG="${INSATLL_DIR}/Mono-MRE-For-CCS.pkg"
STUDIO_PKG="${INSATLL_DIR}/CocosStudio.pkg"
STUDIO_PATH="/Applications/Cocos Studio.app"
if [ -f "${STUDIO_PKG}" ]; then
    sudo installer -pkg "${MONO_PKG}" -target /
    sudo installer -pkg "${STUDIO_PKG}" -target /
    rm -rf "${STUDIO_PKG}"
    rm -rf "${MONO_PKG}"
fi

# invoke the setup.py in engine
SETUP_PY="${INSATLL_DIR}/frameworks/cocos2d-x/setup.py"
python "${SETUP_PY}" -a "" -n "" -t "${INSATLL_DIR}/tools/ant/bin"

# open "${INSATLL_DIR}/Cocos Studio.app"
