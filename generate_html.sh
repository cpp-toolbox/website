#!/bin/bash
python scripts/create_sbpt_html_files.py
python scripts/fast-html/main.py --config-file html/fast_html_config.txt 
python scripts/fsweb/main.py -s fh_generated_html -w -t dark -ifm use -x
cd code
doxygen Doxyfile
cd ..
rm -rf fsweb_generated_dir/docs
cp -r code/doxygen_docs/html fsweb_generated_dir/docs
