crontab -e

\* \* \* \* \* cd /full/path && /usr/bin/python3 /full/path/minecraft_server_status.py >> /full/path/out.txt

The >> /full/path/out.txt is to write script output to
a file (optional).