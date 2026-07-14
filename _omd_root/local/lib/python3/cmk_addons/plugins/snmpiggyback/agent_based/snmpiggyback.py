#!/usr/bin/env python3

import re
import os
import json
from cmk.agent_based.v2 import AgentSection, CheckPlugin, Service, Result, State, Metric, check_levels

def parse_snmpiggyback(string_table):
    linebuffer = []
    hostname = None
    hre = re.compile(r'^\[\[\[\[([a-zA-Z0-9].*?)\]\]\]\]')
    parsed = {}
    for l in string_table:
        line = l[0]
        if hre.match(line):
            if len(linebuffer) > 0:
                parsed[hostname] = linebuffer
                linebuffer = []
                hostname = re.search(hre, line).group(1).replace("/", "_")
            else:
                hostname = re.search(hre, line).group(1).replace("/", "_")
        else:
            linebuffer.append(line.strip())
    parsed[hostname] = linebuffer
    return parsed
    
def parse_snmpiggyback_hoststats(string_table):
    j = ""
    for l in string_table:
        for t in l:
            j = j + " " + t
    parsed = json.loads(j)
    return parsed

def discover_snmpiggyback(section):
    yield Service()
    
def discover_snmpiggyback_hoststats(section):
    yield Service()

def check_snmpiggyback(section):
    # print(section)
    for host in section:
        path = os.environ['OMD_ROOT'] + "/var/check_mk/snmpwalks/" + host
        with open(path, "w") as f:
            for oid in section[host]:
                f.write(oid)
                f.write("\n")
    yield Result(state=State.OK, summary="Everything is fine")
    
def check_snmpiggyback_hoststats(section):
    slices = section["slices"]
    duration = section["duration"]
    yield Result(state=State.OK, summary=f"Informational only, acquired {slices} slices in {duration} seconds.")

agent_section_snmpiggyback = AgentSection(
    name = "snmpiggyback_data",
    parse_function = parse_snmpiggyback,
)

agent_section_snmpiggyback_hoststats = AgentSection(
    name = "snmpiggyback_host_stats",
    parse_function = parse_snmpiggyback_hoststats,
)

check_plugin_snmpiggyback = CheckPlugin(
    name = "snmpiggyback",
    service_name = "SNMPiggyback",
    sections = [ "snmpiggyback_data" ],
    discovery_function = discover_snmpiggyback,
    check_function = check_snmpiggyback,
)

check_plugin_snmpiggyback_hoststats = CheckPlugin(
    name = "snmpiggyback_hoststats",
    service_name = "SNMPiggyback host statistics",
    sections = [ "snmpiggyback_host_stats" ],
    discovery_function = discover_snmpiggyback_hoststats,
    check_function = check_snmpiggyback_hoststats,
)
