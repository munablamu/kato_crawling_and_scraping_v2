#!/bin/bash

cd $(dirname $0)
. ../../scraping/bin/activate

pyqs ebook --loglevel INFO
