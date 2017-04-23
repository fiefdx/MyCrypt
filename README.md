# MyCrypt
(中文文档请参看[这里](#mycrypt_zh))

An application for encrypt & decrypt local files with TEA, and it can do files/folders copy, cut, paste, rename, delete too.
It is more like a file manager base on python and web.

It works like this:
![Alt text](/doc/mycrypt_main_window_en.png?raw=true "mycrypt_main_window")


# Features
1. encrypt and decrypt files with TEA
2. copy, cut, paste, rename, delete files/folders
3. interface support english and chinese
4. it have some random characters insert when encrypt, so every time you encrypt a file, the result .crypt file sha1 may different


# Configuration
MyCrypt/app/configuration.yml
```yaml
APP_DEBUG: false

# LOG_LEVEL
# a value of (NOSET, DEBUG, INFO, WARNING, ERROR, CRITICAL)
# default NOSET
LOG_LEVEL: NOSET

SERVER_HOST: 127.0.0.1
SERVER_PORT: 8000
```


# Installation & Run
You can run it from source, My laptop's OS is Xubuntu 64bit, so I just show how to setup & run it on Xubuntu.

1. from source
   ```bash
   # install pip
   sudo apt-get install python-pip

   # run app/dev.sh
   cd MyCrypt/app
   ./dev.sh

   # install tea package
   # download it from github https://github.com/fiefdx/tea
   tar xzvf ./tea.tar.gz or unzip ./tea.zip
   cd tea
   sudo python ./setup.py install

   # edit the configuration.yml file, before run it.
   # you can try to run MyCrypt.py or MyCryptGUI.py in terminal, check if error occur
   cd MyCrypt/app
   # MyCrypt.py is a terminal application, MyCryptGUI.py is a GUI application(have a system tray icon) based on Wxpython
   python ./MyCrypt.py or python ./MyCryptGUI.py

   # open a web browser, recommend firefox or chrome, open page http://localhost:8000
   # you should see the main window
   ```

# Operations & Screenshots

1. encrypt file
   ![Alt text](/doc/mycrypt_encrypt_password_en.png?raw=true "mycrypt_encrypt_password")

   ![Alt text](/doc/mycrypt_encrypt_encrypting_en.png?raw=true "mycrypt_encrypt_encrypting")

2. decrypt file
   ![Alt text](/doc/mycrypt_decrypt_password_en.png?raw=true "mycrypt_decrypt_password")

   ![Alt text](/doc/mycrypt_decrypt_decrypting_en.png?raw=true "mycrypt_decrypt_decrypting")

3. show original file name
   ![Alt text](/doc/mycrypt_show_original_file_name_en.png?raw=true "mycrypt_show_original_file_name")


<a name="mycrypt_zh"><a>


# MyCrypt
这一个基于python和web的文件加密解密应用，同时也支持文件和文件夹的复制、剪切、粘贴、重命名和删除操作，更像一个简单的文件管理器。

应用主界面如下:
![Alt text](/doc/mycrypt_main_window_zh.png?raw=true "mycrypt_main_window")


# 程序特性
1. 基于TEA算法的文件加密解密
2. 文件和文件夹的复制、剪切、粘贴、重命名和删除操作
3. 界面支持中文和英文
4. 因为在加密中会有随机字符的插入，所以生成的加密文件每一次的sha1可能都不一样


# 程序配置项
配置文件为 MyCrypt/app/configuration.yml
```yaml
APP_DEBUG: false

# LOG_LEVEL
# a value of (NOSET, DEBUG, INFO, WARNING, ERROR, CRITICAL)
# default NOSET
LOG_LEVEL: NOSET

SERVER_HOST: 127.0.0.1
SERVER_PORT: 8000
```


# 安装和运行步骤
你可以从源码直接运行，由于我用的是Xubuntu 64位，所以，就只写一下在Xubuntu下的安装和运行步骤。

1. 从源码运行
   ```bash
   # 安装pip
   sudo apt-get install python-pip

   # 运行app/dev.sh
   cd MyCrypt/app
   ./dev.sh

   # 安装tea包，用来加密笔记内容
   # 从github下载tea https://github.com/fiefdx/tea
   tar xzvf ./tea.tar.gz 或 unzip ./tea.zip
   cd tea
   sudo python ./setup.py install

   # 在运行笔记之前要先更改configuration.yml配置文件
   # 可以在终端中运行MyCrypt.py或者MyCryptGUI.py，观察是否有报错
   cd MyCrypt/app
   # MyCrypt.py是一个终端程序，MyCryptGUI.py是一个基于Wxpython的图形界面程序（会显示一个系统托盘图标）
   python ./MyCrypt.py 或 python ./MyCryptGUI.py

   # 在服务启动后，用浏览器（推荐用火狐或谷歌浏览器）打开http://localhost:8000
   # 应该就可以看到应用主界面了
   ```


# 常见操作和截屏

1. 加密文件
   ![Alt text](/doc/mycrypt_encrypt_password_zh.png?raw=true "mycrypt_encrypt_password")

   ![Alt text](/doc/mycrypt_encrypt_encrypting_zh.png?raw=true "mycrypt_encrypt_encrypting")

2. 解密文件
   ![Alt text](/doc/mycrypt_decrypt_password_zh.png?raw=true "mycrypt_decrypt_password")

   ![Alt text](/doc/mycrypt_decrypt_decrypting_zh.png?raw=true "mycrypt_decrypt_decrypting")

3. 显示原始文件名
   ![Alt text](/doc/mycrypt_show_original_file_name_zh.png?raw=true "mycrypt_show_original_file_name")

