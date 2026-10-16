#def _energy_offset(option, value):
#    # this is a function for DRIVER_OPTIONS
#    # it allows modifying the value before writing it to the log
#    # the name argument is the name of the parameter (eg. Energy)
#    # and the value is the value of the parameter from the PZEM-004T
#    # this function must return a value so that this module can record it in the log
#
#    return value+129000

DEVICE_LABELS={
    # the raw device name will be replaced by the label during log parsing
    # modifying this dict is optional

    #"pzem004t:/dev/ttyUSB0,1": "AC"
}
DRIVER_OPTIONS={
    # driver options for individual devices

    #"pzem004t:/dev/ttyUSB0,1": {
    #    "Energy": _energy_offset
    #}
}

LOG_PARAMS=[
    # define here what parameters from PZEM-004T you want to write to the log

    "Voltage",
    "Current",
    "Power",
    "Energy",
    "Frequency",
    "PowerFactor",
    "Alarm"
]
