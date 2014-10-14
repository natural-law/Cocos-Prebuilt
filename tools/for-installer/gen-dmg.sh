#!/bin/bash
# gen-dmg.sh

PROJ_NAME=$1

WIN_WIDTH=770
WIN_HEIGHT=410

PKG_EXTENSION="mpkg"

BASEDIR="$( cd "$( dirname "$0" )" && pwd )"
RELEASE_DIR="${BASEDIR}/../../release"
PKG_FILE_PATH="${RELEASE_DIR}/${PROJ_NAME}.${PKG_EXTENSION}"
SIGNED_PKG_NAME="${PROJ_NAME}_signed.${PKG_EXTENSION}"
UNSIGNED_PKG_NAME="${PROJ_NAME}_unsigned.${PKG_EXTENSION}"

#check if the app is exist
if [ ! -d "${PKG_FILE_PATH}" ]; then
    echo "The app file ${PKG_FILE_PATH} is not exist. Can't create dmg file!"
    exit 1
fi

TARGET_NAME="${PROJ_NAME}.dmg"
TMP_DIR="/tmp/${PROJ_NAME}"
RES_DIR="${BASEDIR}/installer-proj-mac/resources"

if [ -d "${TMP_DIR}" ]; then
    rm -rf "${TMP_DIR}"
fi

mkdir "${TMP_DIR}"

cp -rf "${PKG_FILE_PATH}" "${TMP_DIR}"

# remove the alias file in pkg
# NEED_REMOVE_FILE="${TMP_DIR}/${PROJ_NAME}.${PKG_EXTENSION}/Contents/Resources/${PROJ_NAME}.pax.gz"
# if [ -f "${NEED_REMOVE_FILE}" ]; then
#     rm -rf "${NEED_REMOVE_FILE}"
# fi

# sign the pkg
productsign --sign "3rd Party Mac Developer Application: CocoaChina (U7E7529TA5)" "${TMP_DIR}/${PROJ_NAME}.${PKG_EXTENSION}" "${TMP_DIR}/${SIGNED_PKG_NAME}"

# rename the pkg files
mv "${TMP_DIR}/${PROJ_NAME}.${PKG_EXTENSION}" "${TMP_DIR}/${UNSIGNED_PKG_NAME}"
mv "${TMP_DIR}/${SIGNED_PKG_NAME}" "${TMP_DIR}/${PROJ_NAME}.${PKG_EXTENSION}"

# create dmg file
pushd "${TMP_DIR}"

"${BASEDIR}/create-dmg/create-dmg" \
    --window-size ${WIN_WIDTH} ${WIN_HEIGHT} \
    --volicon "${RES_DIR}/Icon.icns" \
    --volname "${PROJ_NAME}" \
    --background "${RES_DIR}/dmg_background.jpg" \
    --icon-size 192 \
    --icon "${PROJ_NAME}.${PKG_EXTENSION}" 590 165 \
    "${TARGET_NAME}" "${TMP_DIR}/${PROJ_NAME}.${PKG_EXTENSION}"

popd

if [ ! -d "${RELEASE_DIR}" ]; then
    mkdir "${RELEASE_DIR}"
fi

# remove the old dmg file in release dir
if [ -f "${RELEASE_DIR}/${TARGET_NAME}" ]; then
    rm -rf "${RELEASE_DIR}/${TARGET_NAME}"
fi

# copy the dmg file from tmp to release dir
cp "${TMP_DIR}/${TARGET_NAME}" "${RELEASE_DIR}"

# remove temp files
rm -rf "${TMP_DIR}"
