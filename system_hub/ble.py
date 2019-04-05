#!/usr/bin/python3
from bluepy import btle

from delegate import SensorDelegate, RingerDelegate
from device import Device

CHARACTERISTIC = 37 #ble module in use characteristic for data

def find_system_devices(sensors, ringers, sensor_obj, ringer_obj):
    '''Find NEW devices that are registered in the system

    Args:
        sensors (dict): sensors_from_sqlite
        ringers (dict): ringers_from_sqlite
        sensor_obj (dict): dict of established sensor objects mac:name
        ringer_obj (dict): dict of established ringer objects mac:name

    Returns:
        dict(sensor_mac:name), dict(ringer_mac:name)
    '''

    sensor_macs = {}
    ringer_macs = {}

    devices = []
    try:
        scanner = btle.Scanner()
        devices = scanner.scan(5.0)
    except Exception as e:
        print ("Scanner crashed... Just ignore. Error:" + str(e))
    for dev in devices:
        print ("Device ",dev.addr," (",dev.addrType,"), RSSI=",dev.rssi," dB")

        if dev.addr in sensors and dev.addr not in sensor_obj:
            sensor_macs[dev.addr] = sensors[dev.addr]
        elif dev.addr in ringers and dev.addr not in ringer_obj:
            ringer_macs[dev.addr] = ringers[dev.addr]

    return sensor_macs, ringer_macs

def check_alive(sensor_objs, ringer_objs, callback):
    '''Check if system device is alive - if not or not responding 
    notify that device is lost and remove from connected devices dicts

    Args:
        sensor_objs (dict): mac:sensor_name
        ringer_objs (dict): mac:ringer_name
        callback (func): call this function if not connected
    '''

    print (len(sensor_objs), len(ringer_objs))
    print ("------------")
    for mac, sensor in list(sensor_objs.items()):
        try:
            state = sensor.getState()
            print ('----->', mac, state)
            if state != 'conn':
                raise Exception("state != 'conn'")
        except Exception as e:
            print (str(e))

            sensor.disconnect()
            sensor_objs.pop(mac, None)
            callback(sensor.name, mac, 0)
    print ("-------------\n")

    for mac, ringer in list(ringer_objs.items()):
        try:
            state = ringer.getState()
            print ('----->', mac, state)
            if state == 'disc':
                raise Exception("state == 'disc'")
        except Exception as e:
            print (str(e))

            ringer.disconnect()
            ringer_objs.pop(mac, None)
            callback(ringer.name, mac, 1)
    print ("------------\n\n")

def receive_sensor_msg(ringer_objs):
    '''Deal with received sensor msg

    Args:
        msg (String): msg from sensor
        ringer_objs (dict): mac:Device
    '''

    def deal_with_sensor_msg(msg):
        print ("PROCESSING SENSOR MSG\n")

        if msg == b"ALARM\n":
            print ("ALARM acknowledged")

            for _, ringer in ringer_objs.items():
                ringer.send_message("RING\n")

    return deal_with_sensor_msg

def send_command(recipients, command):
    for _, recipient in recipients:
        recipient.send_message(command)

def create_sensor_objects(data, sensors_objs, ringer_objs):
    '''Create sensor objects

    Args:
        data (dict): mac:name
        sensors_objs (dict): mac:sensor_device
        ringer_objs (dict): mac:ringer_device
    '''

    for mac, name in data.items():
        print ("Creating sensor with: ", mac, name)
        try:
            s_delegate = SensorDelegate(name, receive_sensor_msg(ringer_objs))
            device = Device(name, CHARACTERISTIC, mac, s_delegate)
            device.withDelegate(s_delegate)
            sensors_objs[mac] = device
        except Exception as e:
            print (str(e))
            return 1    #return error code, so rerun scan
    return 0

def create_ringer_objects(data, ringer_objs):
    '''Create ringer object

    Args:
        data (dict): mac:name
        ringer_objs (dict): mac:ringer_device
    '''

    for mac, name in data.items():
        print ("Creating ringer with: ", mac, name)
        try:
            r_delegate = RingerDelegate(name) 
            device = Device(name, CHARACTERISTIC, mac, r_delegate)
            device.withDelegate(r_delegate)
            ringer_objs[mac] = device
        except Exception as e:
            print (str(e))
            return 1    #return error code, so rerun scan
    return 0


