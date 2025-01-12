#!/home/lab/prober/venv/bin/python3

import asyncio
from run_ping import *
from influxdb_write import *



input_data:list[list[str]] = [['vrf0', '10.0.1.1'],
                              ['vrf0', '10.0.10.1'],
                              ['vrf0', '10.0.11.1'],
                              ['vrf0', '10.0.12.1'],
                              ['vrf0', '10.0.13.1'],
                              ['vrf0', '10.0.14.1'],
                              ['vrf0', '10.0.15.1'],]




async def main()->None:

    influxdb_api_token = os.environ.get("INFLUXDB_TOKEN")

    while True:

        commands:list[Any] = []
        for i in range(len(input_data)):
            command_parameters = f'ping -I {input_data[i][0]} {input_data[i][1]} -c 1 -w 1'
            commands.append(run_command(command_parameters))
        ping_result = await asyncio.gather(*commands)
        print(type(ping_result))
        for item in ping_result:
            print(item)

        influxdb_write_data:list[list[str|int]] = []
        for i in range(len(input_data)):
            worklist:list = []
            command_result_value: int = -1
            if ping_result[i][0] == 0:
                command_result_value = 1
            elif ping_result[i][0] == 1:
                command_result_value = 0
            else:
                assert False, "Unexpected return code"    
            worklist.append('natgw')
            worklist.append(input_data[i][0])
            worklist.append(input_data[i][1])
            worklist.append(command_result_value)
            worklist.append(ping_result[i][1])
            influxdb_write_data.append(worklist)

        print(influxdb_write_data)

        response_status_code = write_influxdb_bulk(influxdb_write_data, influxdb_api_token)
        print(response_status_code)

    return


if __name__ == '__main__':
    asyncio.run(main = main())
