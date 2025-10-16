#!/usr/bin/env bash

source /home/gyr/.gyr.d/suse.d/bin/.env
REPOSITORY=images

function usage() {
    printf "Usage: %s [-a api_url]\n" $(basename $0)
}

while getopts "a:" opt; do
    case $opt in
        a)
            API_URL=${OPTARG}
            ;;
        ?)
            usage
            exit 1
            ;;
    esac
done

FILE=~/work/$1
osc -A ${API_URL} ls -b SUSE:Maintenance:$1/patchinfo > ${FILE}
if hash lnav ; then
    LOG_VIEWER=lnav
else
    LOG_VIEWER=vim
fi
${LOG_VIEWER} ~/work/$1
echo ${FILE}
