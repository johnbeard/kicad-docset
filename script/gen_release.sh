#! /bin/bash

# Script to generate KiCad docset releases

DOCSET=$1

GH_PROJ="https://github.com/johnbeard/kicad-docset"
TOKEN=$(cat access_token.txt)

PLIST=${DOCSET}/Contents/Info.plist

VERSION=$(grep -A1 CFBundleVersion ${PLIST} | tail -n1 | perl -pe  's/( *|<.*?>)//g')

TAR_NAME=KiCad.tgz

echo "Doc version: ${VERSION}"
# Tar up the docset
tar --exclude='.DS_Store' -cvzf docsets/${TAR_NAME} -C ${DOCSET}/.. $(basename ${DOCSET})

FEEDFILE=feeds/KiCad-master.xml
RELEASE_URL=${GH_PROJ}/releases/download/${VERSION}/${TAR_NAME}

# Update the feed file
cat > ${FEEDFILE} <<EOL
<entry>
    <version>${VERSION}</version>
    <url>${RELEASE_URL}</url>
</entry>
EOL
