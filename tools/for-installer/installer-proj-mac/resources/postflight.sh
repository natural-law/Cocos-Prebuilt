#!/bin/bash

INSATLL_DIR="/Applications/cocos"
chmod -R a=rwx "${INSATLL_DIR}"

STUDIO_PKG="${INSATLL_DIR}/Cocos Studio.pkg"
STUDIO_PATH="/Applications/Cocos Studio.app"
if [ -f "${STUDIO_PKG}" ]; then
    sudo installer -pkg "${STUDIO_PKG}" -target /
    mv -f "${STUDIO_PATH}" "${INSATLL_DIR}/Cocos Studio.app"
    rm -rf "${STUDIO_PKG}"
fi

open "${INSATLL_DIR}"
