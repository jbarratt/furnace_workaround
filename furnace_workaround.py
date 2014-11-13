#!/usr/bin/env python

import yaml
import os
import nest_thermostat as nest
from nest_thermostat.utils import c_to_f
from time import sleep
from pushover import init, Client
import traceback

with open(os.path.expanduser('~/.nestconfig'), 'r') as f:
    cfg = yaml.load(f.read())


def load_temp():
    if 'temp_cache_file' not in cfg:
        return None

    if not os.path.exists(cfg['temp_cache_file']):
        return None

    return float(open(cfg['temp_cache_file'], 'r').read())


def store_temp(value):
    if 'temp_cache_file' not in cfg:
        return None

    if os.path.exists(cfg['temp_cache_file']):
        os.unlink(cfg['temp_cache_file'])
    open(cfg['temp_cache_file'], 'w').write(str(value))


def manage_temperature():
    n = nest.Nest(cfg['user'], cfg['password'])
    device = n.structures[0].devices[0]

    last_temp = load_temp()
    store_temp(device.temperature)

    if device.temperature > cfg['target_temp']:
        return None

    # If the heat is actually rising, don't mess with it!
    if last_temp and device.temperature > last_temp:
        return None

    # Don't change the temperature unless it's significantly off
    if device.target < (cfg['target_temp']-1):
        device.target = cfg['target_temp']
        return None

    # Check to see if the device temp is critically low
    # This means the furnace may not have lit
    if device.temperature < (device.target - 2):
        # force the furnace to think the heater is off by setting the temp
        # 2 degrees lower than it currently is
        print ("Attempting to relight thermostat.\n"
               "Device temperature was {0}\n"
               "Device target was {1}\n").format(c_to_f(device.temperature),
                                                 c_to_f(device.target))
        device.temperature = (device.temperature - 2)
        sleep(60)
        device.temperature = cfg['target_temp']
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
            break
        except:
            traceback.print_exc()
            sleep(30)

    if not complete:
        notify("Tried to check temp 3 times and failed")


if __name__ == '__main__':
    main()
