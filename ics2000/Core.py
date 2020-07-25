import enum
from typing import Optional
import requests
import json
import ast

from ics2000.Command import *
from ics2000.Utils import *

base_url = "https://trustsmartcloud2.com/ics2000_api/"


def constraint_int(inp, min, max) -> int:
    if inp < min:
        return min
    elif inp > max:
        return max
    else:
        return inp


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
        # self.pulldevices()

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
            decrypted = json.loads(decrypt(device["data"], self.aes))
            if "module" in decrypted and "info" in decrypted["module"]:
                decrypted = decrypted["module"]
                name = decrypted["name"]
                entityid = decrypted["id"]
                if decrypted["device"] not in DeviceType._value2member_map_:
                    self._devices.append(Device(name, entityid, self))
                    return
                dev = DeviceType(decrypted["device"])
                if dev == DeviceType.LAMP:
                    self._devices.append(Device(name, entityid, self))
                if dev == DeviceType.DIMMER:
                    self._devices.append(Dimmer(name, entityid, self))
                if dev == DeviceType.OPENCLOSE:
                    self._devices.append(Device(name, entityid, self))

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

    def dim(self, entity, level):
        cmd = self.getcmddim(entity, level)
        self.sendcommand(cmd.getcommand())

    def zigbee_color_temp(self, entity, color_temp):
        cmd = self.get_zigbee_temp_cmd(entity, color_temp)
        self.sendcommand(cmd.getcommand())

    def zigbee_dim(self, entity, dim_lvl):
        cmd = self.get_zigbee_dim_cmd(entity, dim_lvl)
        self.sendcommand(cmd.getcommand())

    def zigbee_switch(self, entity, power):
        cmd = self.get_zigbee_power(entity, power)
        self.sendcommand(cmd.getcommand())

    def getcmdswitch(self, entity, on) -> Command:
        cmd = self.simplecmd(entity)
        cmd.setdata(
            "{\"module\":{\"id\":" + str(entity) + ",\"function\":0,\"value\":" + (str(1) if on else str(0)) + "}}",
            self.aes)
        return cmd

    def getcmddim(self, entity, level) -> Command:
        cmd = self.simplecmd(entity)
        cmd.setdata(
            "{\"module\":{\"id\":" + str(entity) + ",\"function\":1,\"value\":" + str(level) + "}}",
            self.aes)
        return cmd

    def getlampstatus(self, entity) -> Optional[bool]:
        url = base_url + "/entity.php"
        params = {"action": "get-multiple", "email": self._email, "mac": self.mac.replace(":", ""),
                  "password_hash": self._password, "home_id": self._homeId, "entity_id": "[" + str(entity) + "]"}
        resp = requests.get(url, params=params)
        arr = json.loads(resp.text)
        if len(arr) == 1 and "status" in arr[0] and arr[0]["status"] is not None:
            obj = arr[0]
            dcrpt = json.loads(decrypt(obj["status"], self.aes))
            return dcrpt["module"]["functions"][0] != 0
        else:
            return None

    def get_zigbee_temp_cmd(self, entity, color_temp):
        color_temp = constraint_int(color_temp, 0, 600)
        cmd = self.simplecmd(entity)
        cmd.setdata(
            "{\"module\":{\"id\":" + str(entity) + ",\"function\":9,\"value\":" + str(color_temp) + "}}",
            self.aes)
        return cmd

    def get_zigbee_dim_cmd(self, entity, dim_lvl):
        dim_lvl = constraint_int(dim_lvl, 1, 254)
        cmd = self.simplecmd(entity)
        cmd.setdata(
            "{\"module\":{\"id\":" + str(entity) + ",\"function\":4,\"value\":" + str(dim_lvl) + "}}",
            self.aes)
        return cmd

    def get_zigbee_power(self, entity, on):
        cmd = self.simplecmd(entity)
        cmd.setdata(
            "{\"module\":{\"id\":" + str(entity) + ",\"function\":3,\"value\":" + (str(1) if on else str(0)) + "}}",
            self.aes)
        return cmd

    def simplecmd(self, entityid):
        cmd = Command()
        cmd.setmac(self.mac)
        cmd.settype(128)
        cmd.setmagic()
        cmd.setentityid(entityid)
        return cmd


class DeviceType(enum.Enum):
    LAMP = 1
    DIMMER = 2
    OPENCLOSE = 3


class Device:

    def __init__(self, name, id, hb):
        self._hub = hb
        self._name = name
        self._id = id
        print(str(self._name) + " : " + str(self._id))

    def name(self):
        return self._name

    def turnoff(self):
        cmd = self._hub.getcmdswitch(self._id, False)
        self._hub.sendcommand(cmd.getcommand())

    def turnon(self):
        cmd = self._hub.getcmdswitch(self._id, True)
        self._hub.sendcommand(cmd.getcommand())

    def getstatus(self) -> Optional[bool]:
        return self._hub.getlampstatus(self._id)


class Dimmer(Device):

    def dim(self, level):
        if level < 0 or level > 15:
            return
        cmd = super()._hub.getcmddim(super()._hub, level)
        super()._hub.sendcommand(cmd.getcommand())


def get_hub(mac, email, password) -> Optional[Hub]:
    url = base_url + "/gateway.php"
    params = {"action": "check", "email": email, "mac": mac.replace(":", ""), "password_hash": password}
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        if ast.literal_eval(resp.text)[1] == "true":
            return Hub(mac, email, password)
    return