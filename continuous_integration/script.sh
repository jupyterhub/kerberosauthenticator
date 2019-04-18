#!/usr/bin/env bash

source /opt/conda/bin/activate

cd /working

py.test kerberosauthenticator -vv

flake8 kerberosauthenticator
