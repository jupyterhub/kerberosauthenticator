#!/usr/bin/env bash

. /venv/bin/activate

set -eux

cd /working
python3 -mpytest

# flake8 kerberosauthenticator
