#!/bin/bash

# change the premission of cocos folder
INSATLL_DIR="/Applications/cocos"
chmod -R a=rwx "${INSATLL_DIR}"

# install cocos studio
STUDIO_PKG="${INSATLL_DIR}/Cocos Studio.pkg"
STUDIO_PATH="/Applications/Cocos Studio.app"
if [ -f "${STUDIO_PKG}" ]; then
    sudo installer -pkg "${STUDIO_PKG}" -target /
    mv -f "${STUDIO_PATH}" "${INSATLL_DIR}/Cocos Studio.app"
    rm -rf "${STUDIO_PKG}"
fi

# invoke the setup.py in engine
SETUP_PY="${INSATLL_DIR}/frameworks/cocos2d-x/setup.py"
python "${SETUP_PY}" -a "${INSATLL_DIR}/tools/android-sdk" -n "${INSATLL_DIR}/tools/android-ndk-r9d" -t "${INSATLL_DIR}/tools/ant/bin"

open "${INSATLL_DIR}"
