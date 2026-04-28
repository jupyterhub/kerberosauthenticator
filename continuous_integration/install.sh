#!/usr/bin/env bash

. /venv/bin/activate

set -eu

cd /working
python3 -mpip install -r requirements.txt -r dev-requirements.txt -e .
