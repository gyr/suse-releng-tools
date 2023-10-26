#!/usr/bin/env sh

APIURL='https://api.suse.de/'

function usage() {
    printf "Usage: %s [-A api_url] project/package/repository/arch\n" $(basename $0)
}

while getopts "a:p:s:" opt; do
    case $opt in
        A)
            APIURL=${OPTARG}
            ;;
        ?)
            usage
            exit 1
            ;;
    esac
done

shift $(($OPTIND - 1))
if [ $# -ne 1 ]; then
    usage
    exit 1
fi

IFS=/ read PROJECT PACKAGE REPOSITORY ARCH dump <<< "$1"
if [ -z "$PROJECT" -o -z "$PACKAGE" -o -z "$REPOSITORY" -o -z "$ARCH" ]; then
    PROJECT=$1
    PACKAGE=$2
    REPOSITORY=$3
    ARCH=$4
fi

echo ${PROJECT}/${PACKAGE}:

if [ -z "${PROJECT}" ] ; then
    usage
    exit 1
fi

osc -A ${APIURL} abortbuild ${PROJECT} ${PACKAGE} -r ${REPOSITORY} -a ${ARCH}
sleep 30
osc -A ${APIURL} rebuild ${PROJECT} ${PACKAGE} -r ${REPOSITORY} -a ${ARCH}
