import os
from enum import IntEnum, Enum
from threading import Thread

import flask

try:
    from rpi_rf import RFDevice
except RuntimeError:
    RFDevice = None
except Exception:
    RFDevice = None

from flask import Flask, render_template
from flask import request
from markupsafe import escape
import csv

import numbers

from dotenv import load_dotenv

load_dotenv()

class ENV(Enum):
    IFFIT_API_KEY = os.getenv("IFFIT_API_KEY")


import urllib.request
import urllib.parse


class SENDER(IntEnum):
    GPIO = 2
    REPEAT = 5
    PROTOCOL = 1
    PULSELENGTH = 350
    CODELENGTH = 24


app = Flask(__name__)

if RFDevice:
    rfdevice = RFDevice(SENDER.GPIO)
    rfdevice.enable_tx()
    rfdevice.tx_repeat = SENDER.REPEAT

# CODES (off, on) it means [row][0] is off.

CODES_DICT = {
    "arvuti": (83028, 83029),
    "laualamp": (86100, 86101),
    "kõlarid": (70740, 70741),
    "voodi": (21588, 21589),
}

CODES = (
    (83028, 83029),
    (86100, 86101),
    (70740, 70741),
    (21588, 21589),
)

import time


def get_code(row, state):
    return CODES[int(row) - 1][int(state)]


def parse_commands(raw_commands):
    result = {
        "now": [],
        "later": [],
    }
    commands = raw_commands.split("|")
    for cmd in commands:
        command = cmd.split("_")
        code = 0
        if len(command) > 2:
            result["later"].append(get_code(command[0], command[2]))
        else:
            result["now"].append(get_code(command[0], command[1]))
    return result


def send_cmd(cmd):
    if RFDevice:
        rfdevice.tx_code(cmd, tx_proto=SENDER.PROTOCOL, tx_pulselength=SENDER.PULSELENGTH,
                         tx_length=SENDER.CODELENGTH)


def do_work(cmd):
    print(f"Command sent: {cmd}")
    send_cmd(cmd)


def do_work_sleep(cmds, cb_time):
    time.sleep(cb_time)
    print(f"Command sent: {cmds} after sleep {cb_time}s")
    for cmd in cmds:
        send_cmd(cmd)


def send_commands(raw_commands):
    if raw_commands.get("commands", []):
        parsed_cmds = parse_commands(raw_commands.get("commands", []))
        for cmd in parsed_cmds["now"]:
            do_work(cmd)

    thread_delay = Thread(target=do_work_sleep, kwargs={'cmds': parsed_cmds["later"], "cb_time": raw_commands["delay"]})
    thread_delay.start()

    thread_iffit = Thread(target=do_iffit, kwargs={'cmd': raw_commands["iffit"]})
    thread_iffit.start()


def load_csv():
    shortcuts = {}
    columns = "1,4,3,2".split(",")
    with open('shortcuts.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row_shortcut = []
            for item in columns:
                if row[item] != '':
                    row_shortcut.append(f"{item}_{row[item]}")
            delay_value = 0
            try:
                if row["delay_time"] != '':
                    delay_value = int(row["delay_time"])
            except ValueError:
                pass

            shortcut_value = {
                "commands": "|".join(row_shortcut),
                "delay": delay_value,
                "iffit": row["iffit"]
            }
            shortcuts[row["name"]] = shortcut_value
            for alias in row["alias"].split(","):
                shortcuts[alias.strip()] = shortcut_value

    return shortcuts


def do_iffit(cmd):
    if not cmd:
        return

    url = f"https://maker.ifttt.com/trigger/{cmd}/with/key/{ENV.IFFIT_API_KEY}"
    f = urllib.request.urlopen(url)
    print(f.read().decode('utf-8'))


SHORTCUTS = load_csv()


@app.route("/", methods=["GET"])
def send_433():
    global SHORTCUTS
    shortcut_name = None
    if request.args.get('cmd'):
        shortcut_name = escape(request.args.get('cmd').replace("_", " ").replace("\"", ""))
    if shortcut_name:
        shortcut_commands = SHORTCUTS.get(shortcut_name)
        if not shortcut_commands:
            SHORTCUTS = load_csv()
            shortcut_commands = SHORTCUTS.get(shortcut_name)
            if not shortcut_commands:
                return f"Käsku ei leitud: {shortcut_name}"
        print(f"Selected shortcut name {shortcut_name} : {shortcut_commands}")
        send_commands(shortcut_commands)

        return f"{shortcut_name}"
    SHORTCUTS = load_csv()
    return render_template('index.html', shortcuts=SHORTCUTS)
