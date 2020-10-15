#!/bin/bash

TESTS="step-22 tablehandler test_assembly test_poisson test_hp"
TESTS="test_assembly tablehandler"
sha=`cd dealii;git rev-parse HEAD`
name=`cd dealii;git describe --exact-match HEAD 2>/dev/null`
desc="`cd dealii;git rev-parse --short HEAD;` $name"
time=`cd dealii;git show --quiet --format=%cD HEAD | head -n 1`
basepath=`pwd`

export DEAL_II_NUM_THREADS=1

mkdir -p $basepath/logs/$sha
rm -f $basepath/logs/$sha/*

cd $basepath
BUILDDIR=`mkdir -p build;cd build;pwd`
logfile=$basepath/logs/$sha/build


# only test sha1 that start with "a":
if [[ -n "$name" ]] || [[ "a${sha}" == a* ]];
then
  echo "Testing $sha - $desc" | tee $logfile 
else
  echo "skipping $sha - $desc";
  exit 1
fi

cd $BUILDDIR
echo hi from `pwd` >>$logfile
cmake -G "Ninja" \
      -D DEAL_II_COMPONENT_EXAMPLES=OFF \
      -D DEAL_II_WITH_TASKFLOW=OFF \
      -D CMAKE_BUILD_TYPE=Release \
      -D CMAKE_INSTALL_PREFIX=`pwd`/install \
      $basepath/dealii >>$logfile 2>&1 && nice ninja install >>$logfile 2>&1 || exit -1

cd $basepath

fail=0
for test in $TESTS ; do
  cd $test
  echo "** working on $test" >>$logfile
  rm -fr CMakeCache.txt CMakeFiles Makefile
  cmake -D DEAL_II_DIR=$BUILDDIR/install . >>$logfile 2>&1 || fail=1
  echo $sha >tmp
  echo $test >>tmp
  echo $desc >>tmp
  echo $time >>tmp
  make run 2>>$logfile | grep "^>" >>tmp || fail=1
  cd ..
  cat $test/tmp | python3 render.py record >> $basepath/logs/$sha/summary
  cp $test/tmp $basepath/logs/$sha/$test
done


cat $basepath/logs/$sha/summary

if [ "${fail}" = "1" ]; then
    echo "ERROR. Whole log:"
    cat $logfile
fi
