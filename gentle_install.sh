#!/bin/bash
apt-get -y install g++
apt-get -y install python
apt-get -y install gfortran
apt-get -y install automake autotools-dev make
git clone https://github.com/kdavis-mozilla/openfst.git
cd openfst
./configure
make
make install
cd .. 
git clone https://github.com/kdavis-mozilla/gentle.git
cd gentle/
./install.sh
