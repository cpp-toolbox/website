#!/bin/bash
python scripts/create_sbpt_html_files.py
python scripts/fsweb/main.py -s html -w -t dark -ifm use -x
