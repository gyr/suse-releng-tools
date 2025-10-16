#!/bin/sh

PROJECT=${1:-SUSE:SLE-15-SP3:GA}
COMMENT=${2:-"installcheck: ignore rpm-ndb"}
source /home/gyr/.gyr.d/suse.d/bin/.env

function usage() {
    printf "Usage: %s [-a api_url] -p project -c comment\n" $(basename $0)
}

while getopts "a:p:c:" opt; do
    case $opt in
        a)
            API_URL=${OPTARG}
            ;;
        p)
            PROJECT=${OPTARG}
            ;;
        c)
            COMMENT=${OPTARG}
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

if [ -z "${COMMENT}" ] ; then
    usage
    exit 1
fi

for staging in $(osc -A ${API_URL} ls  | grep  "^${PROJECT}:Staging:") ; do
    osc -A ${API_URL} api "/comments/project/$staging" | grep -q "$COMMENT" || osc -A ${API_URL} api -X POST -d "$COMMENT" "/comments/project/$staging"
done

# osc -A ${API_URL} comment create -c "installcheck: ignore rpm-ndb" project SUSE:SLE-15-SP3:GA:Staging:A
