#!/usr/bin/env bash

source /opt/conda/bin/activate

cd /working

set -xe

py.test kerberosauthenticator -vv

flake8 kerberosauthenticator







python3 -mpytest --disable-warnings -x
python3 -mpytest
