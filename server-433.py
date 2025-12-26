import os
from enum import IntEnum, Enum
from threading import Thread

try:
    # noinspection PyUnresolvedReferences
    from rpi_rf import RFDevice
except RuntimeError:
    RFDevice = None
except Exception:
    RFDevice = None

from bottle import Bottle, template # or route
from markupsafe import escape
import csv

from dotenv import load_dotenv
import urllib.request
import urllib.parse

import tinytuya

load_dotenv()


import time

class ENV(Enum):
    RFDEVICE_GPIO = os.getenv("RFDEVICE_GPIO")
    IFFIT_API_KEY = os.getenv("IFFIT_API_KEY")
    TUYA_LAELAMP_DEVICE_ID=os.getenv("TUYA_LAELAMP_DEVICE_ID")
    TUYA_LAELAMP_LOCAL_KEY=os.getenv("TUYA_LAELAMP_LOCAL_KEY")
    TUYA_LAELAMP_IP=os.getenv("TUYA_LAELAMP_IP")
    TUYA_LAELAMP_VERSION=os.getenv("TUYA_LAELAMP_VERSION")

tuyaLaeLamp =  tinytuya.BulbDevice(
    ENV.TUYA_LAELAMP_DEVICE_ID.value,
    ENV.TUYA_LAELAMP_IP.value,
    ENV.TUYA_LAELAMP_LOCAL_KEY.value,
    version=ENV.TUYA_LAELAMP_VERSION.value
)

tuyaDevices = {
    "laelamp": tuyaLaeLamp,
}



class SENDER(IntEnum):
    GPIO = int(ENV.RFDEVICE_GPIO.value)
    REPEAT = 5
    PROTOCOL = 1
    PULSELENGTH = 350
    CODELENGTH = 24


if RFDevice:
    # noinspection PyCallingNonCallable
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
    thread_now = None
    thread_delay = None

    if raw_commands.get("commands", None):
        parsed_cmds = parse_commands(raw_commands.get("commands", []))

        thread_now = Thread(target=do_work_now, kwargs={'cmds': parsed_cmds["now"]})
        thread_now.start()

        thread_delay = Thread(target=do_work_sleep,
                              kwargs={'cmds': parsed_cmds["later"], "cb_time": raw_commands["delay"]})
        thread_delay.start()

    # thread_iffit = Thread(target=do_iffit, kwargs={'cmd': raw_commands["iffit"]})
    # thread_iffit.start()

    if thread_now:
        thread_now.join()

    thread_tuya = Thread(target=do_tuya, kwargs={'cmd': raw_commands["tuya"]})
    thread_tuya.start()

    if thread_delay:
        thread_delay.join()


def load_csv():
    shortcuts = {}
    columns = "3,1,4,2".split(",")
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
                # "iffit": row["iffit"],
                "tuya": row["tuya"],
            }
            shortcuts[row["name"]] = shortcut_value
            for alias in row["alias"].split(","):
                shortcuts[alias.strip()] = shortcut_value

    return shortcuts


def do_iffit(cmd):
    if not cmd:
        return

    url = f"https://maker.ifttt.com/trigger/{cmd}/with/key/{ENV.IFFIT_API_KEY.value}"
    f = urllib.request.urlopen(url)
    print(f.read().decode('utf-8'))


def do_tuya(cmd):
    if not cmd:
        return

    cmd_device = cmd.split("_")[0]  # Assuming cmd is in the format "device_command"
    command = cmd.split("_")[1]  # Example command: "on" or "off"

    device = tuyaDevices.get(cmd_device)
    if device:
        # Example command: "on" or "off"
        if command == "on":
            device.turn_on()
        elif command == "off":
            device.turn_off()
        else:
            print(f"Unknown command for Tuya device ({cmd_device}) cmd: {cmd}")
    else:
        print(f"Tuya device not found: {cmd_device}")

def do_work_now(cmds):
    for cmd in cmds:
        do_work(cmd)


SHORTCUTS = load_csv()

from bottle_tools.plugins import ReqResp

app = Bottle()
app.install(ReqResp())


@app.get('/')
def send_433(request, response):
    global SHORTCUTS
    shortcut_name = None
    if request.query.cmd:
        shortcut_name = escape(request.query.cmd.replace("_", " ").replace("\"", ""))
    if shortcut_name:
        shortcut_commands = SHORTCUTS.get(shortcut_name)
        if not shortcut_commands:
            SHORTCUTS = load_csv()
            shortcut_commands = SHORTCUTS.get(shortcut_name)
            if not shortcut_commands:
                return f"Command not found: {shortcut_name}"
        print(f"Selected shortcut name {shortcut_name} : {shortcut_commands}")
        send_commands(shortcut_commands)

        return f"{shortcut_name}"
    SHORTCUTS = load_csv()
    return template('index', shortcuts=SHORTCUTS)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5433, debug=True, reloader=True)
