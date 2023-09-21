import datetime
import hashlib
import json
import platform
import re
import threading
import time
from collections import defaultdict
import socket


import requests
#import send_data
from flask import Flask, request

app = Flask(__name__)

data_dict = defaultdict(list)
last_update_time = time.time()
url = "http://146.48.62.97:3000/"


def send_data(temperature):

     ## getting the hostname by socket.gethostname() method
    hostname = socket.gethostname()
    ## getting the IP address using socket.gethostbyname() method
    ip_address = socket.gethostbyname(hostname)
    ## printing the hostname and ip_address
    print(f"Hostname: {hostname}")
    print(f"IP Address: {ip_address}")

    requestor_id = ip_address

    # Get current date and time
    now = datetime.datetime.now()

    # Generate a random hash using SHA-256 algorithm
    hash_object = hashlib.sha256()
    hash_object.update(bytes(str(now), "utf-8"))
    hash_value = hash_object.hexdigest()
    request_id = str(requestor_id) + str(now) + hash_value
    request_id = (
        re.sub("[^a-zA-Z0-9\n\.]", "", request_id)
        .replace("\n", "")
        .replace(" ", "")
    )
    topic_name = "SIFIS:Privacy_Aware_Device_Anomaly_Detection"
    topic_uuid = "Anomaly_Detection"
    temperature_string_list = []

    temperature_string = str(temperature).replace("[", "").replace("]", "")
    temperature_string_list.append(temperature_string)
    print("List of temperatures:", temperature_string_list)
    requestor_type = "NSSD"
    temp_info = {
        "description": "Device Anomaly Detection",
        "requestor_id": str(requestor_id),
        "request_id": str(request_id),
        "requestor_type": str(requestor_type),
        "connected": True,
        "Data Type": "List",
        "Temperatures": temperature_string_list,
    }
    requests.post(
        url + "topic_name/" + topic_name + "/topic_uuid/" + topic_uuid,
        json=temp_info,
    )


def write_log():
    global data_dict
    log_file = open("temperature_log.txt", "a")
    now = time.time()
    for name, temps in data_dict.items():
        if len(temps) >= 48:
            last_48_temps = temps[-48:]
            last_temp = temps[-1]
            log_data = {
                "name": name,
                "last_48_temps": last_48_temps,
                "last_temp": last_temp,
                "timestamp": now,
            }
            log_file.write(json.dumps(log_data) + "\n")
    log_file.close()
    threading.Timer(60.0, write_log).start()  # run again after 2 minutes


def add_last_temps():
    global data_dict
    while time.time() - start_time < 60:
        time.sleep(60 / 48)
        for name, temps in data_dict.items():
            if len(temps) > 0:
                data_dict[name].append(temps[-1])
    threading.Timer(60 / 48, add_last_temps).start()


def check_and_add_temp(name, temperature):
    global data_dict
    if time.time() - start_time < 60:
        data_dict[name].append(temperature)
        if len(data_dict[name]) > 48:
            data_dict[name] = data_dict[name][-48:]
        elif len(data_dict[name]) < 48:
            data_dict[name] = [temperature] * (48 - len(data_dict[name]))
    else:
        if len(data_dict[name]) > 0 and temperature == data_dict[name][-1]:
            return
        if len(data_dict[name]) == 48:
            data_dict[name] = data_dict[name][1:]
        data_dict[name].append(temperature)

        last_47_temps = data_dict[name][-47:]
        last_temp = data_dict[name][-1]
        log_data = {
            "name": name,
            "last_48_temps": last_47_temps,
            "last_temp": last_temp,
            "timestamp": time.time(),
        }
        temp = log_data["last_48_temps"]
        if len(temp) == 48:
            print(len(temp))
            with open("temp4_log.txt", "a") as log_file:
                    log_file.write(json.dumps(log_data) + "\n")
                    send_data(temp)


@app.route("/temperature", methods=["POST"])
def receive_data():
    global last_update_time, data_dict
    data = request.get_json()
    print("\nDATA:")
    print(data)
    name = data.get("name", None)
    temperature = data.get("temperature", None)

    if name is not None and temperature is not None:
        last_update_time = time.time()
        check_and_add_temp(name, temperature)

    return "Data received"


if __name__ == "__main__":
    start_time = time.time()
    threading.Timer(60.0, add_last_temps).start()
    write_log()

    app.run("0.0.0.0", port="6000")