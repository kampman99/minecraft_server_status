from rcon.source import Client # sudo apt install python3-rcon
from email.message import EmailMessage
from email.utils import formatdate

import os
import smtplib
import yaml

cwd = os.getcwd()

yaml_config_file = f'{cwd}/minecraft_server_status_config.yaml'
yaml_data_file = f'{cwd}/minecraft_server_status_data.yaml'

def main():

    mc_server_url, mc_server_rcon_port, rcon_passwd, \
        email_from, email_to, smtp_server, smtp_user, smtp_passwd \
        = get_yaml_config(yaml_config_file)
    
    player_count, response = \
        get_player_count_from_server( \
            mc_server_url, mc_server_rcon_port, rcon_passwd)
    print(f'{player_count=}')
    
    prev_player_count = read_count_from_file()
    print(f'{prev_player_count=}')
    
    if player_count == prev_player_count:
        change = False
    else:
        change = True

    print(f'{change=}')

    if change:
        write_count_to_file(player_count)
        send_email_alert(player_count, prev_player_count, response, \
            email_from, email_to, smtp_server, smtp_user, smtp_passwd)

    print(f'{player_count=} {prev_player_count=} {change=}')

def get_player_count_from_server( \
        mc_server_url, mc_server_rcon_port, rcon_passwd):
    
    # Connect to Minecraft server and run 'list' command
    with Client(mc_server_url, mc_server_rcon_port, passwd=rcon_passwd) as client:
        response = client.run('list')
    print(response)
    # list returns "There are 0 of a max of 8 players online:"
    # Splitting on spaces makes the count element 2
    # Convert to integer from string so it can be compared
    player_count = int(response.split(' ')[2])
    
    return player_count, response

def get_yaml_config(yaml_config_file):
    with open(yaml_config_file, 'r') as file:
        response = yaml.safe_load(file)
        mc_server_url = response['mc_server_url']
        mc_server_port = response['mc_server_rcon_port']
        rcon_passwd = response['rcon_passwd']
        email_from = response['email_from']
        email_to = response['email_to']
        smtp_server = response['smtp_server']
        smtp_user = response['smtp_user']
        smtp_passwd = response['smtp_passwd']

    return mc_server_url, mc_server_port, rcon_passwd, email_from, \
        email_to, smtp_server, smtp_user, smtp_passwd

def read_count_from_file():
    with open(yaml_data_file, 'r') as file:
        response = yaml.safe_load(file)
        try:
            # Get player count from yaml file. Will be a string.
            player_count = int(response['player_count'])
        except:
            # If we can't read the count from the file, assume 0
            # and write it to the file.
            player_count = 0
            write_count_to_file(0)

    return player_count

def send_email_alert(count, prev_count, response,
        email_from, email_to, smtp_server, smtp_user, smtp_passwd):
    message = EmailMessage()
    body = f'Minecraft server player count changed from {prev_count} to {count}.\n\n'
    body += 'Server response: '
    body += response
    message.set_content(body)
    message['Subject'] = 'Minecraft server notification'
    message['From'] = email_from
    message['To'] = email_to
    message["Date"] = formatdate(localtime=True)

    s = smtplib.SMTP_SSL(smtp_server)
    s.login(smtp_user, smtp_passwd)
    s.send_message(message)

def write_count_to_file(count):
    
    # Convert to a yaml object
    data = yaml.safe_load(f'player_count: {str(count)}')

    with open(yaml_data_file, 'w') as file:
        yaml.dump(data, file)

if __name__ == '__main__':
    main()
