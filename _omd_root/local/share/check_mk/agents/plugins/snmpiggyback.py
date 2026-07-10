#!/usr/bin/env python3
# Shebang needed this time to find the interpreter!

# (c) 2025-2026 Mattias Schlenker

# This script expects a configuration file $MK_CONFDIR/snmpiggyback.json
# If not run as agent plugin, it can be specified via --config
#
#{
#    "hosts": [
#        { 
#            "name" : "hp-mattias",
#            "commands" : [ 
#                "snmpwalk -t 20  -O qa -c public -v 1 10.76.23.248 .1.3.6.1.2.1",
#                "snmpwalk -t 20  -O qa -c public -v 1 10.76.23.248 .1.3.6.1.4.1"
#            ]
#        }
#    ]
#}

import requests
import argparse
import os
import time
import json
import sys

def get_cfgfile():
    parser = argparse.ArgumentParser("snmpiggyback")
    parser.add_argument(
        "--config",
        help="Specify the config file to read.",
        type=str
    )
    args = parser.parse_args()
    if args.config:
        return args.config
    if "MK_CONFDIR" in os.environ:
        return os.environ["MK_CONFDIR"] + "/snmpiggyback.json"
    return None

def get_config():
    cfgfile = get_cfgfile()
    if cfgfile is None:
        output = { "error" : "No config specified." }
        print("<<<snmpiggyback_stats:sep(0)>>>")
        print(json.dumps(output))
        exit(0)
    if not os.path.exists(cfgfile):
        output = { "error" : "Non existing config file specified." }
        print("<<<snmpiggyback_stats:sep(0)>>>")
        print(json.dumps(output))
        exit(0)
    with open(cfgfile) as f:
        try:
            config = json.load(f)
        except:
            output = { "error" : "Non parseable config file specified." }
            print("<<<snmpiggyback_stats:sep(0)>>>")
            print(json.dumps(output))
            exit(0)
    return config

def walk_host(cfg):
    print("[[[[" + cfg["name"] + "]]]]")
    sys.stdout.flush()
    for c in cfg["commands"]:
        retval = os.system(c)

def walk_allhosts(cfg):
    print("<<<snmpiggyback_data:sep(0)>>>")
    sys.stdout.flush()
    for h in cfg["hosts"]:
        walk_host(h)
    output = { "success" : "Successfully created SNMPiggyback data." }
    print("<<<snmpiggyback_stats:sep(0)>>>")
    print(json.dumps(output))

config = get_config()
walk_allhosts(config)

