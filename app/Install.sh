#!/bin/bash
cmd_path=$(dirname $0)
cd $cmd_path
./MakeShortcut.sh
sudo cp ./MyCrypt.desktop /usr/share/applications/MyCrypt.desktop