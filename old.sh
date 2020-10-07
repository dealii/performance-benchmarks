#!/bin/bash

# todo: need to clean deal.II build directory

# Run some selected old versions (releases) and apply necessary patches before
# doing so.

cd dealii;git reset --hard -q && git clean -fd -q;cd ..

cd dealii;git checkout v9.2.0;cd ..
rm -rf build
./test.sh

cd dealii;git checkout v9.1.1;cd ..
rm -rf build
./test.sh

cd dealii;git checkout v9.0.1;cd ..
rm -rf build
./test.sh

cd dealii;git checkout v8.5.0;cd ..
rm -rf build
./test.sh


#cd dealii;git checkout v8.4.1;cd ..
#rm -rf build
#./test.sh

#cd dealii;git checkout v8.3.0;cd ..
#rm -rf build
#./test.sh

#cd dealii;git checkout v8.2.1;cd ..
#patch -p1 <patches/821andbefore.patch
#rm -rf build
#./test.sh

# not tested:
#cd dealii;git checkout v8.1.0;cd ..
#patch -p1 <patches/810andbefore.patch
#rm -rf build
#./test.sh

# not tested:
#cd dealii;git checkout v8.0.0;cd ..
#rm -rf build
#./test.sh 
