#!/bin/bash
cmd_path=$(dirname $0)
cd $cmd_path
shortcut="/usr/share/applications/MyCrypt.desktop"
if [ -e $shortcut ]
then
    sudo rm "$shortcut"
fi
sudo rm "/usr/local/bin/mycrypt"
sudo rm "/usr/local/bin/mycryptgui"
sudo rm "/usr/share/pixmaps/mycrypt.png"