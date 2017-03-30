import json
from genieorm import Model, dict_value, Field, ListField, EmbedField


class Wan(Model):
    ip = Field('ExternalIPAddress', dict_value)
    status = Field('ConnectionStatus', dict_value)

    def __repr__(self):
        return "<Wan {0}>".format(self.ip)


class Host(Model):
    ip = Field('IPAddress', dict_value)

    def __repr__(self):
        return "<Host {0}>".format(self.ip)


class Hosts(Model):
    hosts = ListField('InternetGatewayDevice.LANDevice.1.Hosts.Host', Host)


class WlanConfig(Model):
    ssid = Field('SSID', dict_value)

    def __repr__(self):
        return "<Wlanconfig {0}".format(self.ssid)


class Hgw(Model):
    id = Field('_id')
    sn = Field('_deviceId._SerialNumber')
    mac = Field('InternetGatewayDevice.WANDevice.3.WANConnectionDevice.1.WANIPConnection.3.MACAddress', dict_value)
    wan = EmbedField('InternetGatewayDevice.WANDevice.3.WANConnectionDevice.1.WANIPConnection.3', Wan)
    hosts = ListField('InternetGatewayDevice.LANDevice.1.Hosts.Host', Host)
    wlans = ListField('InternetGatewayDevice.LANDevice.1.WLANConfiguration', WlanConfig)


with open("hg.json") as f:
    device = json.load(f)

h = Hgw(device)

print("\nAccess documennt paths")
print(Hgw.wan.ip.path)
print(Hgw.wan.ip.fullpath)
print("\nAccess fields")
print(h.wan.ip)
print(h.hosts)
print("\nDump to json or dict")
print(h.to_json())
print(h.to_dict())
