#! /usr/bin/python3

import yaml
import pprint
from classes import Host
from typing import Any
import logging


logger = logging.getLogger(__name__)





def yaml2dict(filename:str)->dict:
    with open(filename, 'r') as f:
        yaml_dict = yaml.safe_load(f)
    logger.info("Successfully generated dictionary object from yaml config file")
    return yaml_dict    



def yamldata2dataclass(yaml_dict:dict[Any])->list[Host]:
    host_objects:list[Host] = []
    for project in yaml_dict['projects']:
        for k, project_dict in project.items():
            for host in project_dict:
                # print(host['host']['vlan'])
            # print (k)
            # print(v)
            # print('-' * 50)
                host_object = Host(project = k,
                                vlan = int(host['host']['vlan']), 
                                site = host['host']['site'],
                                alias = host['host']['alias'],
                                ipv4addr = host['host']['ipv4addr'],
                                ipv4gw = host['host']['ipv4gw'],
                                ipv6addr = host['host']['ipv6addr'],
                                ipv6gw = host['host']['ipv6gw'],
                                pings = host['host']['pings'])
                # print(host_object)
                host_objects.append(host_object)
    return host_objects



def generate_iproute2_config(host_objects:list[Host], main_int_a: str = 'ens33')->str:
    
    iproute2_config: str = ''
    iproute2_config += f'sudo ip link set dev {main_int_a} up\n'
    for obj in host_objects:
        if obj.site == 'a':
            main_int = main_int_a
        elif obj.site == 'b':
            assert False, 'wrong value'
        else:
            assert False, 'wrong value'      
        iproute2_config += f'sudo ip link add vrf{obj.vlan} type vrf table {obj.vlan}\n'
        iproute2_config += f'sudo ip link set dev vrf{obj.vlan} up\n'
        iproute2_config += f'sudo ip link add link {main_int} name {main_int}.{obj.vlan} type vlan id {obj.vlan}\n'
        iproute2_config += f'sudo ip link set dev {main_int}.{obj.vlan} up\n'
        iproute2_config += f'sudo ip link set dev {main_int}.{obj.vlan} master vrf{obj.vlan}\n'
        for ipv4_address in obj.ipv4addr:
            iproute2_config += f'sudo ip addr add {ipv4_address} dev {main_int}.{obj.vlan}\n'
        iproute2_config += f'sudo ip route add 0.0.0.0/0 via {obj.ipv4gw} vrf vrf{obj.vlan}\n'
        for ipv6_address in obj.ipv6addr:
            iproute2_config += f'sudo ip -6 addr add {ipv6_address} dev {main_int}.{obj.vlan}\n'
        iproute2_config += f'sudo ip -6 route add ::/0 via {obj.ipv6gw} vrf vrf{obj.vlan}\n'
    logger.info("iproute2 config was generated and saved in iproute2_config.txt")
    return iproute2_config    




def string2file(text:str, filename:str)->None:
    with open (filename, 'w') as f:
        f.write(text)



def generate_ping_commands(host_objects:list[Host])->list[list[str]]:
    ping_commands:list[list[str]] = []
    for obj in host_objects:
        for dst in obj.pings:
            # worklist:list[str] = []
            if '.' in dst:
                #this is ipv4
                for obj_ipv4_address in obj.ipv4addr:
                    worklist:list[str] = []
                    cmd = f'ping -I vrf{obj.vlan} -I {obj_ipv4_address.split('/')[0]} {dst} -c 1 -w 1'
                    worklist.append(cmd)
                    worklist.append(f'vrf{obj.vlan}')
                    worklist.append(obj_ipv4_address.split('/')[0])
                    worklist.append(dst)
                    worklist.append(obj.project)
                    ping_commands.append(worklist)

            elif ':' in dst:
                #this is ipv6
                for obj_ipv6_address in obj.ipv6addr:
                    worklist:list[str] = []
                    cmd = f'ping -6 -I vrf{obj.vlan} -I {obj_ipv6_address.split('/')[0]} {dst} -c 1 -w 1'
                    worklist.append(cmd)
                    worklist.append(f'vrf{obj.vlan}')
                    worklist.append(obj_ipv6_address.split('/')[0])
                    worklist.append(dst)
                    worklist.append(obj.project)
                    ping_commands.append(worklist)
            else:
                assert False, 'wrong value'
    return ping_commands



def main()->None:
    filename = 'hosts.yml'
    yaml_dict = yaml2dict(filename)
    pprint.pprint(yaml_dict)
    host_objects:list[Host] = yamldata2dataclass(yaml_dict)
    iproute2_config:str = generate_iproute2_config(host_objects)
    print(iproute2_config)
    string2file(iproute2_config, 'iproute2_config.txt')
    print(generate_ping_commands(host_objects))


if __name__ == '__main__':
    main()
