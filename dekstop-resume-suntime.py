# import required modules
import datetime
from dateutil import tz
import requests
from suntime import Sun

# latitude and longitude fetch
LATITUDE = 58.37
LONGITUDE = 26.76

HOST = "nuti"
ALTHOST = "printer"

COMMAND_SUNDUSK = "pime"

sun = Sun(LATITUDE, LONGITUDE)

sun_rise = sun.get_sunrise_time().time()
sun_set = sun.get_sunset_time().time()

now = datetime.datetime.now(sun_rise.tzinfo).time()

def send_command(command):
    try:
        try:
            send_request(HOST, command)
        except Exception as e:
            print(f"Primary host request failed: {e}")
            send_request(ALTHOST, command)
    except Exception as e:
        print("Both host requests failed:", e)




def send_request(host, command):
    result = requests.get(f"http://{host}.local:5433/?cmd={command}")
    print(f"Command sent: '{command}' to '{host}' response '{result.text}'")

if not (sun_rise <= now <= sun_set):
    send_command(COMMAND_SUNDUSK)