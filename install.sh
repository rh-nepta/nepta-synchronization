#!/bin/bash


function pkg_install {
    local PKG_NAME="$1"
    local CMD='/usr/bin/dnf'

    if ! type "$CMD" &> /dev/null; then
        CMD='/usr/bin/yum'
    fi

    "$CMD" install -y "$PKG_NAME"
}

# Build RPM package using the setuptools bdist_rpm and install it on a system
SYNC_RPM_PKG_TMP_PATH="$(python3 setup.py bdist_rpm 2>/dev/null | grep 'copying\|moving /tmp/' | grep '/RPMS/' | awk '{ print $2; }')"
SYNC_RPM_PKG_NAME="$(basename $SYNC_RPM_PKG_TMP_PATH)"

pkg_install "./rpms/$SYNC_RPM_PKG_NAME"
