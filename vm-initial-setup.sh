#!/usr/bin/env sh
# setup for Leap 15.1
cat  /etc/os-release

# install osc
sudo zypper ref
sudo zypper in osc

# create user
sudo useradd --create-home gyribeiro
sudo passwd gyribeiro

su - gyribeiro

# install osc-plugins
mkdir -v ~/repos ~/.osc-plugins
cd ~/repos
git clone https://gitlab.suse.de/sle-prjmgr/release-management-tools.git
cd ~/.osc-plugins
ln -vs ~/repos/openSUSE-release-tools/osclib
ln -vs ~/repos/openSUSE-release-tools/osc-staging.py

# install pip
cd ~/bin
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
chmod 755 get-pip.py
python3 get-pip.py --user
pip install --user --upgrade pip
pip freeze
pip freeze > pip_fresh_install

# install osc-pluging requeriments
pip install --user colorama
pip install --user pyxdg
