#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

if [ "x${VENV_DIR}" == "x" ];then
    VENV_DIR="${DIR}/../venv"
fi

if [ ! -e ${VENV_DIR} ];then
    mkdir -p ${VENV_DIR}
    virtualenv ${VENV_DIR} --python=python3
fi

. ${VENV_DIR}/bin/activate
export PYTHONPATH=${DIR}/../:${PYTHONPATH}
export DJANGO_SETTINGS_MODULE='findingitems.settings'
