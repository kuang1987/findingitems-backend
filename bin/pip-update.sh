#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

. ${DIR}/activate.sh
pip install -U -r ${DIR}/../requirements.txt