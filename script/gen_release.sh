#! /bin/bash

# Script to generate KiCad docset releases

DOCSET=$1

FEED_NAME="KiCad"

GH_OWNER="johnbeard"
GH_PROJ="kicad-docset"
GH_URL="https://github.com/${GH_OWNER}/${GH_PROJ}"
TOKEN=$(cat access_token.txt)

PLIST=${DOCSET}/Contents/Info.plist

VERSION=$(grep -A1 CFBundleVersion ${PLIST} | tail -n1 | perl -pe  's/( *|<.*?>|-dirty)//g')

TAR_NAME=${FEED_NAME}.tgz

echo "Doc version: ${VERSION}"
# Tar up the docset
tar --exclude='.DS_Store' -cvzf docsets/${TAR_NAME} -C ${DOCSET}/.. $(basename ${DOCSET})

FEEDFILE=feeds/master/{FEED_NAME}.xml
RELEASE_URL=${GH_URL}/releases/download/${VERSION}/${TAR_NAME}

# Update the feed file
cat > ${FEEDFILE} <<EOL
<entry>
    <name>${FEED_NAME}</name>
    <version>${VERSION}</version>
    <url>${RELEASE_URL}</url>
</entry>
EOL

APIURL="https://api.github.com"
token_cmd="Authorization: token ${TOKEN}"
rel_path="repos/${GH_OWNER}/${GH_PROJ}/releases"

# make the release if it doesn't exist

resp=$(curl -H "${token_cmd}" ${APIURL}/${rel_path}/tags/${VERSION})

if [[ $(echo ${resp} | jq ".message") == "\"Not Found\"" ]]; then
    echo "Making release: ${VERSION}"
    data="{\"tag_name\":\"${VERSION}\",\"target_commitish\":\"master\",\"name\":\"${VERSION}\",\"body\":\"\"}"
    release=$( curl -H "$token_cmd" --data ${data} "${APIURL}/${rel_path}" )
    REL_ID=$( echo ${release} | jq '.id')
else
    echo "Release exists"
    REL_ID=$( echo ${resp} | jq '.id')
fi

echo "Release ID: ${REL_ID}"

function upload_asset {

    REL_ID=$1
    FILEPATH=$2

    FILE=$( basename ${FILEPATH} )

    echo "Uploading $FILEPATH as ${FILE}"

    UPLOAD_URL="https://uploads.github.com"
    UL_ASSEST_PATH="repos/${GH_OWNER}/${GH_PROJ}/releases/${REL_ID}/assets?name=${FILE}"

    curl -H "${token_cmd}" -H "Content-Type: application/octet-stream" --data-binary @"${FILEPATH}"  ${UPLOAD_URL}/${UL_ASSEST_PATH}
}

upload_asset ${REL_ID} docsets/${TAR_NAME}
upload_asset ${REL_ID} ${FEEDFILE}
