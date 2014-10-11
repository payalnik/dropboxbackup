#!/usr/bin/python

import os
import sys
import time
import string
from os.path import getsize

curDate = time.strftime("%d.%m.%Y", time.gmtime())
curDay = time.strftime("%d", time.gmtime())
backupDelay = time.time()-86400
if curDay == "01" or curDay == "15" or (len(sys.argv) >1 and sys.argv[1]=='full'):
    backupDelay = 0
    print "Full backup init"
    isfull = True
else:
    isfull = False
    print "Incremental backup init"
    
print "curDate:", curDate

# Include the Dropbox SDK libraries
from dropbox import client, rest, session
from backupcreds import *

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'
sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

oauth_token = ''
oauth_token_secret = ''

try: f = open("dropbox_token.txt",'r')
except: f = False

if f:
  oauth_token = string.strip(f.readline())
  oauth_token_secret = string.strip(f.readline())
  f.close()

print "oauth token found:", oauth_token, oauth_token_secret

if oauth_token == '' or oauth_token_secret == '':
  request_token = sess.obtain_request_token()

  # Authorize the application on dropbox site
  url = sess.build_authorize_url(request_token)
  print "url:", url
  print "Please visit this website and press the 'Allow' button, then hit 'Enter' here."
  raw_input()
  # This will fail if the user didn't visit the above URL and hit 'Allow'
  access_token = sess.obtain_access_token(request_token)
  f = open("dropbox_token.txt","wb")
  f.write(access_token.key + '\n')
  f.write(access_token.secret)
  f.close()
else:
  sess.set_token(oauth_token, oauth_token_secret)

client = client.DropboxClient(sess)
print "linked account:", client.account_info()

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

def sync_dir(dir):
  rootdir = dir
  print "Syncing directory:", rootdir
  startTime = backupDelay
  for root, subFolders, files in os.walk(rootdir):
    for file in files:
      fname = os.path.join(root,file)
      if os.path.getmtime(fname)>startTime:
        #print root, file
        os.system("mkdir -p 'backup"+root+"'")
        cmd = "cp "+shellquote(fname)+" "+shellquote('backup'+fname)
        os.system(cmd)

print "Making dump of MySQL databases..."
if os.system(sqlbackupstr):
    print 'Error creating database dump'
    exit()    

print "Syncing Dirs..."
for dirn in sync_dirs:
    sync_dir(dirn)

if isfull: fullness='.full.'
else: fullness = '.inc.'

backupName = backup_folder_name+curDate+fullness+'.7z'

print "Creating archive with name", backupName
if os.system("7z a -p"+archpass+" "+backupName+" backup/* /etc"):
    print 'Error creating archive file'
    exit()

f = open(backupName,'rb')
if f:
  fsize = getsize(backupName)
  uploader = client.get_chunked_uploader(f, fsize)
  print "Uploading file", fsize, "bytes..."
  while uploader.offset < fsize:
    try:
      upload = uploader.upload_chunked()
      print "."
    except rest.ErrorResponse, e:
      # perform error handling and retry logic
      print "error uploading file!"
      delete_file = False
  uploader.finish("/"+backupName)
  f.close()
  print "File uploaded successfully."

print "Deleting temp files..."
os.system("rm -r backup/*")
if delete_file:
    os.system("rm " + backupName);
