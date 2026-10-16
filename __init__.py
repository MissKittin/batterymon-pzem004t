import sys

if sys.argv[0].endswith("/batterymon.py"):
    import os

    sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

    from .pzem004t_log import *
else:
    from .pzem004t_read import *
