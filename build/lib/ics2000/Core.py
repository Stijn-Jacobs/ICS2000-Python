from typing import Optional
import requests
import json
import ast
from .Command import *

base_url = "https://trustsmartcloud2.com/ics2000_api/"


class Hub:
    aes = None
    mac = None

    def __init__(self, mac, email, password):
        """Initialize an ICS2000 hub."""
        self.mac = mac
        self._email = email
        self._password = password
        self._connected = False
        self._homeId = -1
        self._devices = []
        self.loginuser()
        self.pulldevices()

    def loginuser(self):
        print("Logging in user")
        url = base_url + "/account.php"
        params = {"action": "login", "email": self._email, "mac": self.mac.replace(":", ""),
                  "password_hash": self._password, "device_unique_id": "android", "platform": "Android"}
        req = requests.get(url, params=params)
        if req.status_code == 200:
            resp = json.loads(req.text)
            self.aes = resp["homes"][0]["aes_key"]
            self._homeId = resp["homes"][0]["home_id"]
            if self.aes is not None:
                print("Succesfully got AES key")
                self._connected = True

    def connected(self):
        return self._connected

    def pulldevices(self):
        url = base_url + "/gateway.php"
        params = {"action": "sync", "email": self._email, "mac": self.mac.replace(":", ""),
                  "password_hash": self._password, "home_id": self._homeId}
        resp = requests.get(url, params=params)
        self._devices = []
        for device in json.loads(resp.text):
            self._devices.append(Device(device["data"], self))

    def devices(self):
        return self._devices

    def sendcommand(self, command):
        url = base_url + "/command.php"
        params = {"action": "add", "email": self._email, "mac": self.mac.replace(":", ""),
                  "password_hash": self._password, "device_unique_id": "android", "command": command}
        requests.get(url, params=params)

    def turnoff(self, entity):
        cmd = self.getcmdswitch(entity, False)
        self.sendcommand(cmd.getcommand())

    def turnon(self, entity):
        cmd = self.getcmdswitch(entity, True)
        self.sendcommand(cmd.getcommand())

    def getcmdswitch(self, entity, on: bool) -> Command:
        cmd = Command()
        cmd.setmac(self.mac)
        cmd.settype(128)
        cmd.setmagic()
        cmd.setentityid(entity)
        cmd.setdata(
            "{\"module\":{\"id\":" + str(entity) + ",\"function\":0,\"value\":" + (str(1) if on else str(0)) + "}}",
            self.aes)
        return cmd


class Device:

    def __init__(self, data, hb):
        self._data = data
        self._hub = hb
        self._name = None
        self._id = None
        decrypted = json.loads(decrypt(data, hb.aes))
        if "module" in decrypted:
            decrypted = decrypted["module"]
            self._name = decrypted["name"]
            self._id = decrypted["id"]
            print(str(self._name) + " : " + str(self._id))

    def name(self):
        return self._name

    def turnoff(self):
        cmd = self._hub.getcmdswitch(self._id, False)
        self._hub.sendcommand(cmd.getcommand())

    def turnon(self):
        cmd = self._hub.getcmdswitch(self._id, True)
        self._hub.sendcommand(cmd.getcommand())


def hub(mac, email, password) -> Optional[Hub]:
    url = base_url + "/gateway.php"
    params = {"action": "check", "email": email, "mac": mac.replace(":", ""), "password_hash": password}
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        if ast.literal_eval(resp.text)[1] == "true":
            return Hub(mac, email, password)
    return

