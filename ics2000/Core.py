import enum
import requests
import json
import ast

from ics2000.Command import *
from ics2000.Devices import *

base_url = "https://trustsmartcloud2.com/ics2000_api/"


def constraint_int(inp, min_val, max_val) -> int:
    if inp < min_val:
        return min_val
    elif inp > max_val:
        return max_val
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
            decrypted = json.loads(decrypt(device["data"], self.aes))
            if "module" in decrypted and "info" in decrypted["module"]:
                decrypted = decrypted["module"]
                name = decrypted["name"]
                entityid = decrypted["id"]

                devices = [item.value for item in DeviceType]
                if decrypted["device"] not in devices:
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
        cmd = self.simplecmd(entity, 0, 0)
        self.sendcommand(cmd.getcommand())

    def turnon(self, entity):
        cmd = self.simplecmd(entity, 0, 1)
        self.sendcommand(cmd.getcommand())

    def dim(self, entity, level):
        cmd = self.simplecmd(entity, 1, level)
        self.sendcommand(cmd.getcommand())

    def zigbee_color_temp(self, entity, color_temp):
        color_temp = constraint_int(color_temp, 0, 600)
        cmd = self.simplecmd(entity, 9, color_temp)
        self.sendcommand(cmd.getcommand())

    def zigbee_dim(self, entity, dim_lvl):
        dim_lvl = constraint_int(dim_lvl, 1, 254)
        cmd = self.simplecmd(entity, 4, dim_lvl)
        self.sendcommand(cmd.getcommand())

    def zigbee_switch(self, entity, power):
        cmd = self.simplecmd(entity, 3, (str(1) if power else str(0)))
        self.sendcommand(cmd.getcommand())

    def get_device_status(self, entity) -> []:
        url = base_url + "/entity.php"
        params = {"action": "get-multiple", "email": self._email, "mac": self.mac.replace(":", ""),
                  "password_hash": self._password, "home_id": self._homeId, "entity_id": "[" + str(entity) + "]"}
        resp = requests.get(url, params=params)
        arr = json.loads(resp.text)
        if len(arr) == 1 and "status" in arr[0] and arr[0]["status"] is not None:
            obj = arr[0]
            dcrpt = json.loads(decrypt(obj["status"], self.aes))
            if "module" in dcrpt and "functions" in dcrpt["module"]:
                return dcrpt["module"]["functions"]
        return []

    def getlampstatus(self, entity) -> Optional[bool]:
        status = self.get_device_status(entity)
        if len(status) >= 1:
            return True if status[0] == 1 else False
        return False

    def simplecmd(self, entity, function, value):
        cmd = Command()
        cmd.setmac(self.mac)
        cmd.settype(128)
        cmd.setmagic()
        cmd.setentityid(entity)
        cmd.setdata(
            "{\"module\":{\"id\":" + str(entity) + ",\"function\":" + str(function) + ",\"value\":" + str(value) + "}}",
            self.aes)
        return cmd


class DeviceType(enum.Enum):
    LAMP = 1
    DIMMER = 2
    OPENCLOSE = 3


def get_hub(mac, email, password) -> Optional[Hub]:
    url = base_url + "/gateway.php"
    params = {"action": "check", "email": email, "mac": mac.replace(":", ""), "password_hash": password}
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        if ast.literal_eval(resp.text)[1] == "true":
            return Hub(mac, email, password)
    return

