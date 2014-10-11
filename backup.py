#!/usr/bin/python

import os
import sys
import time
import string
from os.path import getsize
import traceback

def sendmail_exit(msg):
    import smtplib
    from email.mime.text import MIMEText
    
    print msg
    print 'Sending Mail...'
    msg = MIMEText(msg)
    msg['Subject'] = 'Error with Dropbox Backup'
    msg['From'] = mail_from
    msg['To'] = mail_to
    
    try:
      s = smtplib.SMTP('localhost')
      s.sendmail(me, [you], msg.as_string())
      s.quit()
    except: print 'Error sending mail'
    exit()

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

# Include the Dropbox SDK libraries
from dropbox import client, rest, session
from config import *

def dropbox_auth():
# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
  ACCESS_TYPE = 'app_folder'
  sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

  if os.path.isfile("dropbox_token.txt"):
    f = open("dropbox_token.txt",'r')
    oauth_token = string.strip(f.readline())
    oauth_token_secret = string.strip(f.readline())
    print "Oauth token found:", oauth_token, oauth_token_secret
    f.close()
    sess.set_token(oauth_token, oauth_token_secret)

  else:
    request_token = sess.obtain_request_token()
    # Authorize the application on dropbox site
    url = sess.build_authorize_url(request_token)
    print "Please visit this website and press the 'Allow' button, then hit 'Enter' here."
    print url
    raw_input()
    # This will fail if the user didn't visit the above URL and hit 'Allow'
    access_token = sess.obtain_access_token(request_token)
    f = open("dropbox_token.txt","wb")
    f.write(access_token.key + '\n')
    f.write(access_token.secret)
    f.close()

  return client.DropboxClient(sess)

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

def backupdb():
  return os.system(sqlbackupstr)

def backupdirs():
  for dirn in sync_dirs:
      if sync_dir(dirn):
        return True
  return False

def createarch():
  if isfull: fullness='.full'
  else: fullness = '.inc'

  backupName = backup_folder_name+curDate+fullness+'.7z'

  print "Creating archive with name", backupName
  if os.system("7z a -p"+archpass+" "+backupName+" backup/* /etc"):
    return False
  else:
    return backupName

def copytodropbox(client,backupName):
  f = open(backupName,'rb')
  if f:
    fsize = getsize(backupName)
    uploader = client.get_chunked_uploader(f, fsize)
    print "Uploading file", fsize, "bytes..."
    while uploader.offset < fsize:
      upload = uploader.upload_chunked()
    uploader.finish("/"+backupName)
    f.close()
    print "File uploaded successfully."

def cleanup(backupName):
  os.system("rm -r backup/*")
  if delete_file:
      os.system("rm " + backupName)

if __name__ == "__main__":

  curDate = time.strftime("%d.%m.%Y", time.gmtime())
  curDay = time.strftime("%d", time.gmtime())
  backupDelay = time.time()-86400
  if curDay == "01" or curDay == "15" or (len(sys.argv) >1 and sys.argv[1]=='full'):
      backupDelay = 0
      print "Full backup init"
      isfull = True
  else:
      print "Incremental backup init"
      isfull = False
      
  print "Current Date:", curDate

  try: 
    dclient = dropbox_auth()
    print "Linked account:", dclient.account_info()[u'email']
  except: sendmail_exit(traceback.format_exc())

  if not os.path.exists('backup'): os.makedirs('backup')

  print "Making dump of MySQL databases..."
  if backupdb(): sendmail_exit("Error making DB backup")
  
  print "Syncing Dirs..."
  if backupdirs(): sendmail_exit("Error syncing dirs")
  
  backupname = createarch()
  if not backupname: sendmail_exit("Error creating archive")
  
  try: copytodropbox(dclient,backupname)
  except : sendmail_exit(traceback.format_exc())

  print "Deleting temp files..."  
  cleanup(backupname)
