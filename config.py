APP_KEY = ''
APP_SECRET = ''

sqlbackupstr = "mysqldump --all-databases -uUSERNAME -pPASS -r backup/backup.sql"
backup_folder_name = 'backup_'
delete_file = False
archpass = ''

sync_dirs = [
"/var/www",
"/home/payalnik/"
]