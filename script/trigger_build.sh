#! /bin/bash

# Script to generate KiCad docset releases

usage='usage: trigger_build.sh [options] <branch> <docset>
     --help                     Print usage plus more detailed help.

     -n --dryrun                Do not perform the upload
     branch                     The release branch
     docset                     Path to pre-generated docset
'

help="$usage"'
Example to trigger a build on the Github CI system
    gen_release.sh master ~/path/to/generated/KiCad.docset
'

die() {
    echo "$@" 1>&2; exit 1
}

# Parse command-line arguments.
help=false

while test "$#" != 2; do
    case "$1" in
    --help | -h)
        help=true
        ;;
    --) shift ; break ;;
    -*) die "$usage" ;;
    *) break ;;
    esac
    shift
done

if [ "$help" = true ]; then
    echo "${usage}"
    exit 0
fi

FEED_NAME="KiCad"

GH_OWNER="johnbeard"
GH_PROJ="kicad-docset"
GH_URL="https://github.com/${GH_OWNER}/${GH_PROJ}"
TOKEN=$(cat access_token.txt)

APIURL="https://api.github.com"
token_cmd="Authorization: token ${TOKEN}"
content_type_header="Accept: application/vnd.github.everest-preview+json"
rel_path="repos/${GH_OWNER}/${GH_PROJ}/dispatches"

# make the release if it doesn't exist

echo "Triggering build"
data="{\"event_type\":\"on-demand-build\"}"
ret=$( curl -H "$token_cmd" -H "${content_type_header}" --data ${data} "${APIURL}/${rel_path}" )
echo ${ret}
