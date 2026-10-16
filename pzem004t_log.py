import os
import importlib
from datetime import datetime
from . import pzem004t_common

def _get_driver(driver_name):
    return importlib.import_module(
        ".pzem004t_drv_"+driver_name,
        package=__package__
    )

def setup(
    WORK_DIR, DEVICES,
    LOG_PARAMS_IGNORE, LOG_PARAMS,
    DUMP_RAW_JSON_IGNORE,
    orig_get_bms_json_data, orig_post_log, orig_log_finish
):
    global _CURRENT_OUT
    global _CURRENT_OUT_TMP
    global _DEVICES

    _CURRENT_OUT=WORK_DIR+"/pzem004t.txt"
    _CURRENT_OUT_TMP=WORK_DIR+"/pzem004t.txt.tmp"

    def get_bms_json_data(device):
        if not device.startswith("pzem004t:"):
            return orig_get_bms_json_data(device)

        if device not in _DEVICES:
            return ({}, "")

        return (_DEVICES[device].get_data(), "")

    def post_log(device, data):
        orig_post_log(device, data)

        if not device.startswith("pzem004t:"):
            return

        try:
            with open(_CURRENT_OUT_TMP, "a") as log:
                try:
                    if "_exception" in data:
                        log.write(datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                        +   " EX "+device+" "+str(data["_exception"]).replace("\n", "\\n")+"\n"
                        )

                        return

                    output_line="OK "+device

                    for param in pzem004t_common.LOG_PARAMS:
                        output_line+=" "+str(
                            data.get(param, "-1")
                        )

                    log.write(datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                    +   " "+output_line+"\n"
                    )
                except(Exception) as e:
                    log.write(datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                    +   " EX "+device+" "+str(e).replace("\n", "\\n")+"\n"
                    )
        except(Exception):
            pass

    def log_finish():
        orig_log_finish()

        try:
            os.replace(_CURRENT_OUT_TMP, _CURRENT_OUT)
        except(Exception):
            pass

    for device in DEVICES:
        if not device.startswith("pzem004t:"):
            continue

        LOG_PARAMS_IGNORE[device]=LOG_PARAMS
        DUMP_RAW_JSON_IGNORE.append(device)

        port, slave_id=device.split(":", 1)[1].split(",", 1)
        options=pzem004t_common.DRIVER_OPTIONS.get(device, {})

        _DEVICES[device]=_get_driver(
            options.get("_driver_name", "default")
        ).pzem004t_drv_configure(
            WORK_DIR,
            port, int(slave_id),
            options
        )

    return (get_bms_json_data, post_log, log_finish)

# init
_CURRENT_OUT=None
_CURRENT_OUT_TMP=None
_DEVICES={}
