#!/usr/bin/env python3.7
import sys
import config
from prettytable import PrettyTable


def get_dict():
    return config.maps


inp = sys.stdin.readline().strip()
if inp in config.maps:
    print(config.maps[inp])
elif inp == "list":
    t = PrettyTable(["Key", "Path"])
    t.align["Key"] = "l"
    t.align["Path"] = "l"
    for key, val in config.maps.items():
        t.add_row([key, val])
    print(t)
elif inp == "keylist":
    for key in config.maps.keys():
        print(key)
else:
    print(config.home)
