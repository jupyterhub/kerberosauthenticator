#!/usr/bin/env bash
source /opt/conda/bin/activate

conda install -c conda-forge \
    jupyterhub \
    pykerberos \
    pytest \
    flake8 \
    notebook \
    requests-kerberos

pip install pytest-asyncio

cd /working

python setup.py develop
