#!/home/lab/prober/venv/bin/python3

import requests
import time
from datetime import datetime
import random
import os
import logging

logger = logging.getLogger(__name__)



def write_influxdb_value(tag:str, field:str, value:int, influxdb_api_token:str)->int:
    url: str = 'http://172.17.0.2:8086/api/v2/write?org=lab&bucket=icmp_probes&precision=ns'

    headers: dict[str] = {'Content-Type': 'text/plain',
            'Accept': 'application/json',
            'Authorization': f'Token {influxdb_api_token}'}

    measurement: str = 'ping'
    influxdb_timestamp: int = int(time.time()) * 1_000_000_000
    data: str = f'{measurement},tag={tag} field={value} {influxdb_timestamp}'
    response = requests.post(url=url, headers=headers, data=data)
    return response.status_code


def write_influxdb_bulk(influxdb_bulk_data: list[list[str|int]], influxdb_api_token: str)->int:
    # influxdb_api_token: str = 'VmP9i7ec7OvFQta-D0O4Mv7pRqEFO4pLzHz8EbsF9Erc5mDlrIvqEKV_c6qccljQKNB6sNc3Vt6pFcbSO-O7OQ=='
    url: str = 'http://172.17.0.2:8086/api/v2/write?org=lab&bucket=icmp_probes&precision=ns'

    headers: dict[str] = {'Content-Type': 'text/plain',
            'Accept': 'application/json',
            'Authorization': f'Token {influxdb_api_token}'}
    data: str = ''
    for index, item in enumerate(influxdb_bulk_data):
        data += f'{item[0]},tag={item[1]} {item[2]}={item[3]} {item[4]}'
        if index < len(influxdb_bulk_data) - 1:
            data += '\n'

    response = requests.post(url=url, headers=headers, data=data)
    logger.info(f'(len(influxdb_bulk_data) entries have been sent to InfluxDB, response code is {response.status_code})')
    return response.status_code




def main()->None:
    influxdb_api_token = os.environ.get("INFLUXDB_TOKEN")
    # print(influxdb_api_token)
    
    # for i in range(301):
    #     response_status_code = write_influxdb_value(tag='vrf0', field='10.0.1.1', value=random.randint(0,1))
    #     print(response_status_code)
    #     time.sleep(1)

    for i in range(301):
        influxdb_timestamp: int = int(time.time()) * 1_000_000_000
        influxdb_bulk_data: list[list[str|int]] = [['ping', 'vrf0', '10.0.1.1', random.randint(0,1), influxdb_timestamp],
                                                   ['ping', 'vrf0', '10.0.1.11', random.randint(0,1), influxdb_timestamp],
                                                   ['ping', 'vrf0', '10.0.1.12', random.randint(0,1), influxdb_timestamp]]
        response_status_code = write_influxdb_bulk(influxdb_bulk_data, influxdb_api_token)
        print(response_status_code)
        time.sleep(1)

    return


if __name__ == '__main__':
    main()
