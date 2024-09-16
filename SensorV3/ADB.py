import re
import subprocess
from time import sleep

def adb_devices():
    adb_call = subprocess.run(["adb", "devices"], text=True, capture_output=True)
    res = adb_call.stdout
    validation = 0
    index = 0
    while index < len(res):
        index = res.find('device', index + 1)
        if index == -1:
            break
        validation += 1
    if validation == 1:
        status = -1
    elif validation == 2:
        status = 0
    else:
        status = 1
    return status


def adb_apps(word):
    status = 0
    adb_call = subprocess.run(["adb", "shell", "pm", "list", "packages", "-e", "-U"], text=True, capture_output=True)
    res = adb_call.stdout.split("\n")
    filtered = []
    for elt in res:
        if word != "":
            if word in elt:
                name = elt[8:]
                filtered.append(name)
        else:
            name = elt[8:]
            filtered.append(name)
        if elt.find('error') != -1:
            status = -1

    return filtered, status


def adb_start_app(app):
    no_uid = app.split(" ")
    status = 0
    adb_call = subprocess.run(["adb", "shell", "monkey", "-p", no_uid[0], "-c", "android.intent.category.LAUNCHER", "1"], text=True, capture_output=True)
    res = adb_call.stdout
    if res.find('error') != -1:
        status = -1
    print("Starting " + no_uid[0])
    return status


def adb_stop_app(package):
    status = 0
    no_uid = package.split(" ")
    adb_call = subprocess.run(["adb", "shell", "am", "force-stop", no_uid[0]], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = adb_call.stdout
    if res.find('error') != -1:
        status = -1
    return status


def adb_dumpsys_power_profile():
    adb_call = subprocess.run(["adb", "shell", "dumpsys", "batterystats", "--power-profile"], text=True, capture_output=True)
    res = adb_call.stdout
    return res

