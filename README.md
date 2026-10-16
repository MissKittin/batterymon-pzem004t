# BatteryMon PZEM-004T
BatteryMon plugin that reads data from the PZEM-004T and saves it to a file.  
The plugin creates a virtual device and handles reading parameters from the module, writing data to an `/tmp/.batterymon/pzem004t.txt`, and parsing data from that file.  
Tested on Raspberry Pi Zero W, Peacefair PZEM-004T V4 and CH340 USB-TTL.  
**Note:** the file contains only the last series of readings.

### Software requirements
* BatteryMon v1.0
* MinimalModbus  
	tested on MinimalModbus 2.1.1 and PySerial 3.5

### Setup
Clone the repository into the BatteryMon program's `batterymon_lib` directory and install the required packages:
```
cd /usr/local/share/batterymon/batterymon_lib
git clone 'https://github.com/MissKittin/batterymon-pzem004t.git' pzem004t
cd pzem004t
pip install -t . minimalmodbus
```

Next, create an `pzem004t_common.py` file and enter your configuration, e.g.:
```
from .pzem004t_common_example import *

def _energy_offset(option, value):
    return value+129000

DEVICE_LABELS.update({
    "pzem004t:/dev/ttyUSB0,1": "AC"
})
DRIVER_OPTIONS.update({
    "pzem004t:/dev/ttyUSB0,1": {
        "Energy": _energy_offset
    }
})

LOG_PARAMS.remove("Alarm") # do not log the Alarm parameter
```
Configuration options are described in the `pzem004t_common_example.py` file.

With all that in place, hook up the plugin in the `batterymon_common.py` file:
```
from . import pzem004t

DEVICES.extend([
    "pzem004t:/dev/ttyUSB0,1" # pzem004t plugin
])

# add this block at the end of the file
get_bms_json_data, post_log, log_finish=pzem004t.setup(
    WORK_DIR, DEVICES,
    LOG_PARAMS_IGNORE, LOG_PARAMS,
    DUMP_RAW_JSON_IGNORE,
    get_bms_json_data, post_log, log_finish
)
```

### Integration with BatteryMon HTTPd
The plugin provides data as a dictionary. You can expose it via BatteryMon HTTPd as JSON.  
You simply need to create a symbolic link from `/usr/local/share/batterymon/batterymon_lib/pzem004t` to `/usr/local/share/batterymon-httpd/share/lib_pzem004t` and add a route to the HTTP server.  
Example route code looks like this:
```
import json
from . import lib_pzem004t as pzem004t

import sys
sys.path.insert(1, "/usr/local/share/batterymon")
from batterymon_lib import batterymon_common
from batterymon_lib import batterymon_helpers
from batterymon_lib import batterymon_helpers_extra

def handle_get(response, request_path, send_response):
    if request_path != "/pzem004t":
        return False

    try:
        send_response(
            200, {"Content-Type": "application/json"},
            json.dumps(pzem004t.get_log())
        )
    except(Exception):
        send_response(500)

    return True

# init - pzem004t
pzem004t.setup_read(
    batterymon_common,
    batterymon_helpers,
    batterymon_helpers_extra
)
```

You can also integrate the PZEM-004T with the `read-voltage.py` tool from the batterymon-extras repository, e.g.:
```
import json
from . import lib_pzem004t as pzem004t

import sys
sys.path.insert(1, "/usr/local/share/batterymon-extras")
import read_voltage

def handle_get(response, request_path, send_response):
    if request_path != "/read-voltage":
        return False

    try:
        data=read_voltage.get_voltage_data(_read_voltage_context, False)
        data["pzem004t"]=pzem004t.get_log()

        send_response(
            200, {"Content-Type": "application/json"},
            json.dumps(data)
        )
    except(Exception):
        send_response(500)

    return True

# init
_read_voltage_context=read_voltage.get_context()

# init - pzem004t
pzem004t.setup_read(
    _read_voltage_context["common"],
    _read_voltage_context["helpers"],
    _read_voltage_context["helpers_extra"]
)
```

### Drivers
The drivers allow for modifying the logic in case the driver provided in the repository does not work.  
The repository provides the `default` driver. For testing purposes, you can run `pzem004t_drv_default.py` to test reading parameters from the PZEM-004T.
