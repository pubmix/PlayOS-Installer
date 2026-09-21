#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 -m venv .runtime
.runtime/bin/python -m pip install -r requirements.txt
.runtime/bin/python app.py
