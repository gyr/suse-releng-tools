#!/usr/bin/env bash

source /home/gyr/.gyr.d/suse.d/bin/.env

function usage() {
    printf "Usage: %s [-a api_url] -p project\n" $(basename $0)
}

while getopts "a:p:t:" opt; do
    case $opt in
        a)
            API_URL=${OPTARG}
            ;;
        p)
            PROJECT=$OPTARG
            ;;
        ?)
            usage
            exit 1
            ;;
    esac
done

if [ -z "${PROJECT}" ] ; then
    usage
    exit 1
fi

set -e
set -x

BUILD_PROJECT=Devel:ReleaseManagement:MUTestBuild
SP=$(echo ${PROJECT} | cut -d ":" -f2 | cut -d "-" -f3)
LOCAL_DIR=${HOME}/work/${SP}
LIST_GA_PACKAGES=${LOCAL_DIR}/15${SP}pkg-$(date -Is)
GA_PROJCONF=${LOCAL_DIR}/ga.proj

ga-packages-list-all.py -p ${PROJECT} > ${LIST_GA_PACKAGES}
# delta 15SP5pkg-2022-10-28T20:07:07-03:00 ${LIST_GA_PACKAGES}
osc -A ${API_URL} meta prjconf ${PROJECT} > ${GA_PROJCONF}
cat ${LIST_GA_PACKAGES} >> ${GA_PROJCONF}
osc -A ${API_URL} meta prjconf ${BUILD_PROJECT} -F ${GA_PROJCONF}
#osc -A ${API_URL} rebuildpac ${BUILD_PROJECT} -f
