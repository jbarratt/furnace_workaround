#!/usr/bin/env python

import yaml
import os
import nest_thermostat as nest
from nest_thermostat.utils import c_to_f
from time import sleep
from pushover import init, Client
import traceback

# in celcius. 65.5 F
TARGET_TEMP = 19
with open(os.path.expanduser('~/.nestconfig'), 'r') as f:
    cfg = yaml.load(f.read())


def manage_temperature():
    n = nest.Nest(cfg['user'], cfg['password'])
    device = n.structures[0].devices[0]

    if device.temperature > TARGET_TEMP:
        return None

    if device.target < TARGET_TEMP:
        device.target = TARGET_TEMP
        return None

    # Check to see if the device temp is critically low
    # This means the furnace may not have lit
    if device.temperature < (device.target - 2):
        # force the furnace to think the heater is off by setting the temp
        # 2 degrees lower than it currently is
        print "Attempting to relight thermostat"
        device.temperature = (device.temperature - 2)
        sleep(60)
        device.temperature = TARGET_TEMP
        return ("Temp is {0}, attempted to relight "
                "thermostat.").format(c_to_f(device.temperature))


def notify(message):
    init(cfg['pushover_api'])
    client = Client(cfg['pushover_user'])
    client.send_message(message, title="Cat Alert")


def main():
    complete = False
    for _ in range(3):
        try:
            message = manage_temperature()
            complete = True
            if message:
                notify(message)
            continue
        except:
            traceback.print_exc()
            sleep(30)

    if not complete:
        notify("Tried to check temp 3 times and failed")


if __name__ == '__main__':
    main()
