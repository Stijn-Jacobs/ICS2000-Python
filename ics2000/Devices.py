from typing import Optional


class Device:

    def __init__(self, name, entity_id, hb):
        self._hub = hb
        self._name = name
        self._id = entity_id
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