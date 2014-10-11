dropboxbackup
=============

A script to back up folders from your UNIX machine to Dropbox.

1. Create an app here https://www.dropbox.com/developers/apps (Dropbox API app, then Files and Datastores)
1. Copy app key and secret to config file
1. Create a folder and put script and config files there
1. Run the script to authorize app
1. Add a bash script that runs the script to /etc/cron.daily
