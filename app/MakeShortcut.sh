#!/bin/bash
cmd_path=$(dirname $0)
cd $cmd_path
cmd_path=`pwd`
mycrypt_path="$cmd_path/MyCrypt"
mycryptgui_path="$cmd_path/MyCryptGUI"
icon_path="$cmd_path/static/mycrypt.ico"

if [ ! -e $mycrypt_path ]
then
    mycrypt_path="$cmd_path/MyCrypt.py"
fi

if [ ! -e $mycryptgui_path ]
then
    mycryptgui_path="$cmd_path/MyCryptGUI.py"
fi

sudo ln -sf "$mycrypt_path" "/usr/local/bin/mycrypt"
sudo ln -sf "$mycryptgui_path" "/usr/local/bin/mycryptgui"
sudo cp -f "$icon_path" "/usr/share/pixmaps/mycrypt.png"

touch ./MyCrypt.desktop
content="[Desktop Entry]
Name=MyCrypt
Comment=MyCrypt
Exec=mycryptgui
Icon=mycrypt
Type=Application
Terminal=false
Categories=GNOME;GTK;Utility;Network;Office;"
echo -e "$content" > ./MyCrypt.desktop
sudo chmod +x ./MyCrypt.desktop