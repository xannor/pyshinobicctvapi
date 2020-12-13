#!/bin/sh

CWD=`pwd`
cd `dirname $0`

pip install -e ..
cd $CWD