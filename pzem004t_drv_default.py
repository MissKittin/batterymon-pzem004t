#!/usr/bin/env python3

import os
import minimalmodbus
import fcntl

class pzem004t_drv:
    def __init__(
        self, work_dir,
        device, slave_id,
        voltage, current, power, energy, frequency, power_factor, alarm
    ):
        self._work_dir=work_dir

        self._device=device
        self._slave_id=slave_id

        self._voltage=voltage
        self._current=current
        self._power=power
        self._energy=energy
        self._frequency=frequency
        self._power_factor=power_factor
        self._alarm=alarm

    def open(self):
        self._pzem=minimalmodbus.Instrument(self._device, self._slave_id)

        self._pzem.serial.baudrate=9600
        self._pzem.serial.bytesize=8
        self._pzem.serial.parity=minimalmodbus.serial.PARITY_NONE
        self._pzem.serial.stopbits=1
        self._pzem.serial.timeout=1
        self._pzem.mode=minimalmodbus.MODE_RTU
        self._pzem.clear_buffers_before_each_transaction=True

    def close(self):
        if hasattr(self, "_pzem"):
            self._pzem.serial.close()
            del self._pzem

    def get_data_raw(self):
        #return {
        #    "Voltage": self._voltage("Voltage", 230.1),
        #    "Current": self._current("Current", 0.253),
        #    "Power": self._power("Power", 50.2),
        #    "Energy": self._energy("Energy", 100),
        #    "Frequency": self._frequency("Frequency", 50.1),
        #    "PowerFactor": self._power_factor("PowerFactor", 0.56),
        #    "Alarm": self._alarm("Alarm", 0)
        #}

        try:
            self.open()

            voltage=self._pzem.read_register(0x0000, 1, functioncode=4)
            current=self._pzem.read_register(0x0001, 3, functioncode=4)
            power=self._pzem.read_register(0x0003, 1, functioncode=4)

            # LOW WORD in 0x0005, HIGH WORD in 0x0006
            low=self._pzem.read_register(0x0005, 0, functioncode=4)
            high=self._pzem.read_register(0x0006, 0, functioncode=4)
            energy=(high << 16) | low

            frequency=self._pzem.read_register(0x0007, 1, functioncode=4)
            power_factor=self._pzem.read_register(0x0008, 2, functioncode=4)
            alarm=self._pzem.read_register(0x0009, 0, functioncode=4)

            return {
                "Voltage": self._voltage("Voltage", voltage),
                "Current": self._current("Current", current),
                "Power": self._power("Power", power),
                "Energy": self._energy("Energy", energy),
                "Frequency": self._frequency("Frequency", frequency),
                "PowerFactor": self._power_factor("PowerFactor", power_factor),
                "Alarm": self._alarm("Alarm", alarm)
            }
        finally:
            self.close()

    def get_data(self):
        with open(
            self._work_dir+"/.pzem004t-"+os.path.basename(self._device)+".lock",
            "a"
        ) as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)

            try:
                return self.get_data_raw()
            except(Exception) as e:
                return {
                    "_exception": e
                }

def _dummy_wrapper(option, value):
    return value

def pzem004t_drv_configure(
    WORK_DIR,
    port, slave_id,
    options
):
    return pzem004t_drv(
        WORK_DIR,
        port, slave_id,
        options.get("Voltage", _dummy_wrapper),
        options.get("Current", _dummy_wrapper),
        options.get("Power", _dummy_wrapper),
        options.get("Energy", _dummy_wrapper),
        options.get("Frequency", _dummy_wrapper),
        options.get("PowerFactor", _dummy_wrapper),
        options.get("Alarm", _dummy_wrapper)
    )

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: "+sys.argv[0]+" /dev/devicename [int-slave-id]")
        sys.exit(1)

    slave_id=1

    if len(sys.argv) > 2:
        slave_id=int(sys.argv[2])

    values=pzem004t_drv_configure(
        None,
        sys.argv[1], slave_id,
        {}
    ).get_data_raw()

    print("Voltage: "+str(values["Voltage"])+" V")
    print("Current: "+str(values["Current"])+" A")
    print("Power: "+str(values["Power"])+" W")
    print("Energy: "+str(values["Energy"])+" Wh")
    print("Frequency: "+str(values["Frequency"])+" Hz")
    print("PowerFactor: "+str(values["PowerFactor"]))
    print("Alarm: "+str(values["Alarm"]))
