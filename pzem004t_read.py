from . import pzem004t_common

class _batterymon_common:
    LOG_PARAMS=pzem004t_common.LOG_PARAMS
    LOG_PARAMS_IGNORE={}

def setup(
    WORK_DIR, DEVICES,
    LOG_PARAMS_IGNORE, LOG_PARAMS,
    DUMP_RAW_JSON_IGNORE,
    orig_get_bms_json_data, orig_post_log, orig_log_finish
):
    for device in DEVICES:
        if not device.startswith("pzem004t:"):
            continue

        LOG_PARAMS_IGNORE[device]=LOG_PARAMS

    return (orig_get_bms_json_data, orig_post_log, orig_log_finish)

def setup_read(
    batterymon_common,
    batterymon_helpers,
    batterymon_helpers_extra
):
    global _CURRENT_OUT
    global _batterymon_helpers
    global _batterymon_helpers_extra

    _CURRENT_OUT=batterymon_common.WORK_DIR+"/pzem004t.txt"
    _batterymon_helpers=batterymon_helpers
    _batterymon_helpers_extra=batterymon_helpers_extra

    _batterymon_helpers.parse_log_line(None, True) # initialize parse_log_line cache

    for device in batterymon_common.DEVICES:
        if not device.startswith("pzem004t:"):
            continue

        batterymon_common.LOG_PARAMS_IGNORE[device]=batterymon_common.LOG_PARAMS
        batterymon_common.DUMP_RAW_JSON_IGNORE.append(device)

        _batterymon_helpers_extra.log_line_dict_cache(device, _batterymon_common, "_pzem004t_", True) # initialize log_line_dict cache

def get_log(ignore_errors=True):
    output=[]

    try:
        with open(_CURRENT_OUT, "r") as log:
            for line in log:
                try:
                    parsed_log_line_dict=_batterymon_helpers_extra.log_line_dict(
                        _batterymon_helpers.parse_log_line(line),
                        _batterymon_common,
                        "_pzem004t_"
                    )

                    if ignore_errors and parsed_log_line_dict["_pzem004t_status"] != "OK":
                        continue

                    if "_pzem004t_device" in parsed_log_line_dict:
                        parsed_log_line_dict["_pzem004t_device"]=pzem004t_common.DEVICE_LABELS.get(
                            parsed_log_line_dict["_pzem004t_device"],
                            parsed_log_line_dict["_pzem004t_device"]
                        )

                    output.append(parsed_log_line_dict)
                except(Exception):
                    pass
    except(Exception):
        return None

    return output

# init
_CURRENT_OUT=None
_batterymon_helpers=None
_batterymon_helpers_extra=None
