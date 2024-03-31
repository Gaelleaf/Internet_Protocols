import subprocess
import re
import json
import platform
import requests
from urllib import request
from urllib.error import URLError
from prettytable import PrettyTable

def get_args(count, info):
    try:
        as_number = info['org'].split()[0][2::]
        provider = " ".join(info['org'].split()[1::])
    except:
        as_number, provider = '*', '*'
    return [f"{count}.", info['ip'], info['country'], as_number, provider]

def get_bogon_args(count, info):
    return [f"{count}.", info['ip'], '*', '*', '*']

def is_complete(text_data):
    return 'Trace complete' in text_data or 'Трассировка завершена' in text_data

def is_timed_out(text_data):
    return 'Request timed out' in text_data or 'Превышен интервал ожидания' in text_data

def is_beginning(text_data):
    return 'Tracing route' in text_data or 'Трассировка маршрута' in text_data

def is_invalid_input(text_data):
    return 'Unable to resolve' in text_data or 'Не удается разрешить' in text_data

table = PrettyTable()
table.field_names = ["number", "ip", "country", "AS number", "provider"]

tracert_proc = subprocess.Popen(["tracert", input('Enter address: ')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

number = 0
for raw_line in iter(tracert_proc.stdout.readline, ''):
    line = raw_line.decode(platform.system().lower() == 'windows' and 'cp866' or 'utf-8')
    ip = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)

    if is_complete(line):
        print(table)
        break
    if is_invalid_input(line):
        print('invalid input')
        break
    if is_beginning(line):
        print(line)
        continue
    if is_timed_out(line):
        print('request timed out')
        continue
    if ip:
        number += 1
        print(f'{"".join(ip)}')
        try:
            info = requests.get(f'https://ipinfo.io/{ip[0]}').json()
            if 'bogon' in info:
                table.add_row(get_bogon_args(number, info))
            else:
                table.add_row(get_args(number, info))
        except URLError:
            table.add_row(get_bogon_args(number, {'bogon': True}))