APP_KEY = ''
APP_SECRET = ''

sqlbackupstr = "mysqldump --all-databases -uUSERNAME -pPASS -r backup/backup.sql"
backup_folder_name = 'backup_'
delete_file = False
archpass = ''
mail_from = ''
mail_to = ''


sync_dirs = [
"/var/www",
"/home/payalnik/"
]