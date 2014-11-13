# Background

I currently have a flaky heater. When it turns on sometimes, it doesn't actually light.
However, it's intermittent, so the techs have had a very hard time figuring it out.

This is a problem because if the temperature is below the target temp, the furnace
will try and light, and the thermostat will think it's asking for the heat to be on.
If the heat's not on, the thermostat won't turn off and on again.

This is even more a problem because when we leave on trips, our cats are home
alone. And even more a problem than that, because it gets below freezing
where I live from time to time. And I love my kitties and don't want them
to be catsicles.

# Method

This tool will run periodically, and if the nest is more than 3 degrees below
the target temp, it will assume it's in an error state; shut it down, wait one
minute, and attempt to turn it back on.

* load a locally stored target temp
* if the target temp == the current nest target temp
    * if the current temp more than 3 degrees less
        * set target temp to 2 degrees less than that
        * wait 1 minute
        * set the target temp back to target
        * send a push notification
* else, set the target temp

# Installing

The requirements are listed in requirements.txt.
The official pip version of nest_thermostat is not ideal, so I used a fork
(actually a fork of a fork)

[https://github.com/jkoelker/nest_thermostat](https://github.com/jkoelker/nest_thermostat)

Beyond that, Just run the script.
You need a config file (currently hardcoded to `~/.nestconfig`) which is
in YAML. `target_temp` should be in celsius, which is the nest's native
mode. (It makes it saner to detect if it's set where we expected.)

```
---
user: user@example.com
password: somepass
target_temp: 19
pushover_api: 01234
pushover_user: 56789
```

Then run the script from a cron, say, every 30 minutes.
