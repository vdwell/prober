#! /usr/bin/python3

import asyncio
import run_ping
import influxdb_write
import yaml2config
import os
from typing import Any
from classes import Host
import time

import logging

logger = logging.getLogger(__name__)



def check_all_success(complex_list: list[tuple[int|str]])->bool:
    worklist:list[int] = []
    for item in complex_list:
        worklist.append(item[0])
    return not any(worklist)    


async def main()->None:

    logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("application.log"),
        # logging.StreamHandler()  # Optionally log to console as well
    ])
    logger = logging.getLogger(__name__)
    logger.info("Starting the main application")

    filename = 'hosts.yml'
    yaml_dict = yaml2config.yaml2dict(filename)
    host_objects:list[Host] = yaml2config.yamldata2dataclass(yaml_dict)
    iproute2_config:str = yaml2config.generate_iproute2_config(host_objects)
    yaml2config.string2file(iproute2_config, 'iproute2_config.txt')

    ping_commands: list[str] = yaml2config.generate_ping_commands(host_objects)
    print(ping_commands)

    influxdb_api_token = os.environ.get("INFLUXDB_TOKEN")


    while True:

        commands:list[Any] = []
        for i in range(len(ping_commands)):
            # print(ping_commands[i])
            # command_parameters = f'ping -I {input_data[i][0]} {input_data[i][1]} -c 1 -w 1'
            commands.append(run_ping.run_command(ping_commands[i][0]))
        ping_result = await asyncio.gather(*commands)
        # print(type(ping_result))
        # for item in ping_result:
        #     print(item)

        influxdb_write_data:list[list[str|int]] = []
        for i in range(len(ping_commands)):
            worklist:list = []
            command_result_value: int = -1
            if ping_result[i][0] == 0:
                command_result_value = 1
            elif ping_result[i][0] == 1:
                command_result_value = 0
            else:
                assert False, "Unexpected return code"    
            worklist.append(ping_commands[i][4])
            worklist.append(f'From_{ping_commands[i][1]}#{ping_commands[i][2]}')
            worklist.append(f'To_{ping_commands[i][3]}')
            worklist.append(command_result_value)
            worklist.append(ping_result[i][1])
            influxdb_write_data.append(worklist)

        # print(influxdb_write_data)
        logger.info(f'Data to write to InfluxDB: {influxdb_write_data}')

        response_status_code = influxdb_write.write_influxdb_bulk(influxdb_write_data, influxdb_api_token)
        # print(response_status_code)
        # logger.info(f'InfuxDB REST API response code is {response_status_code}')

        if check_all_success(ping_result):
            time.sleep(1)


if __name__ == '__main__':
    asyncio.run(main = main())
