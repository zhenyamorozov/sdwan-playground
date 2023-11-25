import os
import json
import tabulate
from dotenv import load_dotenv

from vmanage.api.authentication import Authentication
from vmanage.api.device import Device

# Prints a pretty table of devices with selected columns
def print_device_table(devices):
    print(json.dumps(devices, indent=4))
    headers = {
        'host-name': "Host-Name",
        'deviceType': "Device Type",
        'uuid': "Device ID",
        'system-ip': "System IP",
        'site-id': "Site ID",
        'version': "Version",
        'deviceModel': "Device Model"
    }
    table = []
    for device in devices:
        if all(k in device for k in headers.keys()):
            table.append([device[i] for i in headers.keys()])
    try:
        print(tabulate.tabulate(table, headers=headers.values(), tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        print(tabulate.tabulate(table, headers=headers.values(), tablefmt="grid"))




load_dotenv(override=True)

vmanage_host = os.environ.get("VMANAGE_HOST")
vmanage_username = os.environ.get("VMANAGE_USERNAME")
vmanage_password = os.environ.get("VMANAGE_PASSWORD")

# print(vmanage_host, vmanage_username, vmanage_password)

#
# Authenticate with vManage. Must specify host, username and password explicitly
#
session = Authentication(
    host=vmanage_host, 
    user=vmanage_username, 
    password=vmanage_password
    ).login()
# Check JSESSIONID cookie
print(session.cookies.get_dict())

#
# Get devices
#
device = Device(session, vmanage_host)
device_list = device.get_device_list(category="vedges")
#print(device_list)
print_device_table(device_list)

#
# Dealing with configuration templates
# Swap feature templates in a device template
#
from vmanage.api.device_templates import DeviceTemplates
from vmanage.api.feature_templates import FeatureTemplates

# Retrieve available device templates as a dict
device_templates = DeviceTemplates(session, vmanage_host)
device_templates_dict = device_templates.get_device_template_dict()
print(json.dumps(device_templates_dict, indent=4))

# Retrieve available feature templates as a dict
feature_templates = FeatureTemplates(session, vmanage_host)
feature_templates_dict = feature_templates.get_feature_template_dict()
print(json.dumps(feature_templates_dict, indent=4))

# Find old and new feature templates IDs
old_template_name = "emorozov-aaa-template"
new_template_name = "emorozov-aaa-new-template"
device_template_name = "emorozov-c8000v-template"
old_template_id = feature_templates_dict[old_template_name]["templateId"]
new_template_id = feature_templates_dict[new_template_name]["templateId"]
# switch old template ID to new template ID in the device template
for generalTemplate in device_templates_dict[device_template_name]["generalTemplates"]:
    if generalTemplate["templateId"] == old_template_id:
        generalTemplate["templateId"] = new_template_id
# add own device template name into the dict (required by the API call)
device_templates_dict[device_template_name]["templateName"] = device_template_name
# make the call to update device template
res = device_templates.update_device_template(device_templates_dict[device_template_name])

#
# Attach a device to device template
#
attach_device_name = "Branch_01"
# find device by its name
attach_device = [i for i in device_list if "host-name" in i and i["host-name"]==attach_device_name][0]
pass