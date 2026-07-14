#!/usr/bin/env python3
# Shebang needed this time to find the interpreter!

# (c) 2026 Mattias Schlenker

# This script expects a configuration file $MK_CONFDIR/snmpiggyback.json
# If not run as agent plugin, it can be specified via --config
#
# {
#    "hosts": [
#        { 
#            "name" : "hp-mattias",
#            "command_template" : "snmpget -t 10  -O nQet -c public -v 1 10.76.23.248",
#            "slicesize" : 30,
#            "samplewalk" : "/tmp/hp_mattias.snmp"
#        }
#    ]
# }
#
# /tmp/hp_mattias.snmp includes either just a list of OIDs or the snmpwalk as created by Checkmk
#
#.1.3.6.1.2.1.1.1.0 HP Color Laser MFP 178 179; V3.82.01.11     AUG-27-2020;Engine V1.00.14 2019-03-04;NIC V6.01.01;S/N CNB3P1XJ4C
#.1.3.6.1.2.1.1.2.0 .2.1773528503.909192755.774778418.926494770.842413878.808466488.808530480.775305006.825111346.774779446
#.1.3.6.1.2.1.1.3.0 197223210
#.1.3.6.1.2.1.1.4.0 Administrator
#.1.3.6.1.2.1.1.5.0 HPF80DACEC4A5F
#.1.3.6.1.2.1.1.6.0 
#.1.3.6.1.2.1.1.7.0 104

import argparse
import os
import time
import json
import sys
import subprocess
import re

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

def walk_slice(cfg, oidlist):
    command = cfg["command_template"] + " " + " ".join(oidlist)
    # print(command)
    sp = subprocess.run(command, shell=True, text=True, capture_output=True)
    for l in sp.stdout.splitlines():
        line = re.sub(r"\s=\s", " ", l)
        #line = re.sub(r"\s\"", " ", line)
        #line = re.sub(r"\"$", "", line)
        print(line)

def walk_host(cfg):
    # sys.stdout.flush()
    print("[[[[" + cfg["name"] + "]]]]")
    oidlist = []
    with open(cfg["samplewalk"], "r") as fh:
        for line in fh:
            oidlist.append(line.split()[0])
            if len(oidlist) % cfg["slicesize"] == 0:
                walk_slice(cfg, oidlist)
                oidlist = []
    walk_slice(cfg, oidlist)
        
def walk_allhosts(cfg):
    print("<<<snmpiggyback_data:sep(0)>>>")
    # sys.stdout.flush()
    for h in cfg["hosts"]:
        walk_host(h)
    output = { "success" : "Successfully created SNMPiggyback data." }
    print("<<<snmpiggyback_stats:sep(0)>>>")
    print(json.dumps(output))

config = get_config()
walk_allhosts(config)
