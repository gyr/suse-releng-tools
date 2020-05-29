#!/bin/sh
VERSION=$1
CODESTREAM=$(echo $1 | sed -e 's/-.*//g')
if [ "$CODESTREAM" == "15" ]; then
    for i in $(osc -A https://api.suse.de/ api "/build/SUSE:SLE-$VERSION:GA/_result?package=000product&multibuild=1&repository=images&arch=local&view=binarylist"  | grep "binary filename" | grep "DVD\|cd-cd\|Packages\|Online\|Full" | grep "Media1.iso\"" | sed -e 's/\(.*\)filename="\(.*.iso\).*/\2/g' | grep x86_64) ; do
        #echo $i | sed -e 's/-\(DVD-.*\)*x86_64-/:\t\t/g;s/-Media.*iso//'
        echo $i | sed -e 's/-x86_64-/:\t\t/g;s/-Media.*iso//'
    done
else
    for i in  $(osc -A https://api.suse.de/ ls SUSE:SLE-$VERSION:GA | grep _product | grep 'DVD-x86\|cd-cd.*x86_64' ) ; do osc -A https://api.suse.de/ ls -b SUSE:SLE-$VERSION:GA $i images local | grep 'Media1.iso$\|Media.iso$' | sed -e 's/-DVD-.*x86_64-/:\t\t/g;s/-Media.*iso//' ; done
fi

KIWI_TEMPLATE=$(osc -A https://api.suse.de ls  SUSE:SLE-$VERSION:GA:TEST | grep kiwi-templates );
for i in $(osc -A https://api.suse.de cat  SUSE:SLE-$VERSION:GA:TEST $KIWI_TEMPLATE _multibuild | grep flavor | sed -e 's,.*<flavor>,,g;s,</.*,,g') ; do
    osc -A https://api.suse.de ls -b  SUSE:SLE-$VERSION:GA $KIWI_TEMPLATE:$i images | grep '.packages$' | sed -e 's/\.packages//' 
done
echo
for i in $(osc -A https://api.suse.de ls SUSE:SLE-$VERSION:GA:TEST | grep -v _product | grep -v 000product | grep -v kiwi ); do 
    osc -A https://api.suse.de ls -b  SUSE:SLE-$VERSION:GA:TEST $i images | grep '.packages$' | sed -e 's/\.packages//' 
done

for i in $(osc -A https://api.suse.de ls  SUSE:SLE-$VERSION:GA:TEST | grep $VERSION-Vagrant ); do
    for j in $(osc -A https://api.suse.de cat  SUSE:SLE-$VERSION:GA:TEST $i _multibuild | grep flavor | sed -e 's,.*<flavor>,,g;s,</.*,,g') ; do
        osc -A https://api.suse.de ls -b  SUSE:SLE-$VERSION:GA $i:$j images | grep '.packages$' | sed -e 's/\.packages//' 
    done
done
