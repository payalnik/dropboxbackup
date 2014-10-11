dropboxbackup
=============

Based on http://habrahabr.ru/post/236483/

Backs up a list of folders, /etc and MySQL databases and moves into Dropbox.

Full updates on 1th and 15th of each months + incremental daily updates.

You need to have 7z and mysqldump installed on your machine.

1. Install Dropbox SDK to run the script: pip install dropbox
1. Create an app here https://www.dropbox.com/developers/apps (Dropbox API app, with access to Files and Datastores)
1. Copy app key and secret to config.py
1. Create a folder and put script and config files there
1. Set up DB password, list of folders to backup and email for error messages in config.py
1. Run the script to authorize app the first time
1. Add a bash script that runs the script to /etc/cron.daily
