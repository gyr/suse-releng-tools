#!/usr/bin/env bash

APIURL='https://api.suse.de/'
REPOSITORY=images

function usage() {
    printf "Usage: %s [-a api_url]\n" $(basename $0)
}

while getopts "a:" opt; do
    case $opt in
        a)
            APIURL=${OPTARG}
            ;;
        ?)
            usage
            exit 1
            ;;
    esac
done

FILE=~/work/$1
osc -A ${APIURL} ls -b SUSE:Maintenance:$1/patchinfo > ${FILE}
if hash lnav ; then
    LOG_VIEWER=lnav
else
    LOG_VIEWER=vim
fi
${LOG_VIEWER} ~/work/$1
echo ${FILE}
