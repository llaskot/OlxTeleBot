It works from 09.00 to 23.00 here @olx_cat_bot (https://t.me/olx_cat_bot)

Install on the linux server:

clone repository

cd to the project directory

create file "creds.py" with a single row:     token = 'your telegram bot token'

create and setup a virtual environment:
1. python3 -m venv venv
2. source venv/bin/activate
3. pip install - r requirements.txt
4. wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
5. sudo dpkg -i google-chrome-stable_current_amd64.deb
6. sudo apt-get install -
   
start app: python3 main.py

