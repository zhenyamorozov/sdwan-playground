import os
import requests
import json
from dotenv import load_dotenv

load_dotenv(override=True)

vmanage_host = os.environ.get("VMANAGE_HOST")
vmanage_username = os.environ.get("VMANAGE_USERNAME")
vmanage_password = os.environ.get("VMANAGE_PASSWORD")

base_uri = f"https://{vmanage_host}/dataservice"

# 1. Get auth cookie
resp = requests.post(
    f"https://{vmanage_host}/j_security_check",
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
    },
    data=f"j_username={vmanage_username}&j_password={vmanage_password}",
    verify=False
)
j_session_id = resp.cookies['JSESSIONID']
cookies = resp.cookies

# 2. Get XSRF token
resp = requests.get(
    base_uri + "/client/token",
    cookies=cookies,
    verify=False
)
xsrf_token = resp.text

# 3. Get devices
resp = requests.get(
    base_uri + "/device",
    cookies=cookies,
    verify=False
)

devices = resp.json()['data']

# 4. Get device reboot history - Real-Time Monitoring
deviceId = devices[0]['deviceId']   # device IP address is used, not uuid
resp = requests.get(
    base_uri + f"/device/reboothistory?deviceId={deviceId}",
    cookies=cookies,
    verify=False
)
rebootHistory = resp.json()['data']

# 5. Get device reboot information - Configuration - Device Actions
resp = requests.get(
    base_uri + f"/device/action/reboot?deviceId={deviceId}",
    cookies=cookies,
    verify=False
)
rebootInformation = resp.json() # The result does not actually contain reboot history

# 6. Get multiple devices reboot information
# This request does not work, although documentation suggests deviceId may be an array
deviceIds = [device['deviceId'] for device in devices]
resp = requests.get(
    base_uri + "/device/action/reboot?deviceId={}".format(",".join(deviceIds)),
    cookies=cookies,
    verify=False
)
# rebootHistory = resp.json()['data']

# 7. Request device reboot
# This request additionally requires XSRF token
deviceToReboot = [device for device in devices if device['device-type']=="vedge"][0] # select a vEdge to reboot
resp = requests.post(
    base_uri + "/device/action/reboot",
    headers={
        "Content-Type": "application/json",
        "X-XSRF-TOKEN": xsrf_token
    },
    data=json.dumps({
        "action": "reboot",
        "deviceType": deviceToReboot['device-type'],
        "devices": [
            {"deviceIP": deviceToReboot['deviceId'], 
            "deviceId": deviceToReboot['uuid']}
        ]
    }),
    cookies=cookies,
    verify=False
)
rebootId = resp.json()['id']


pass