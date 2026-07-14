#!/usr/bin/env python3

import re
import os
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

def discover_snmpiggyback(section):
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

agent_section_snmpiggyback = AgentSection(
    name = "snmpiggyback_data",
    parse_function = parse_snmpiggyback,
)

check_plugin_snmpiggyback = CheckPlugin(
    name = "snmpiggyback",
    service_name = "SNMPiggyback",
    sections = [ "snmpiggyback_data" ],
    discovery_function = discover_snmpiggyback,
    check_function = check_snmpiggyback,
)
