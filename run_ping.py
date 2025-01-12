#!/home/lab/prober/venv/bin/python3
import asyncio
from typing import Any
import time

async def run_command(cmd)->int:
    influxdb_timestamp: int = int(time.time()) * 1_000_000_000
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode} at {influxdb_timestamp} time]')
    # if stdout:
    #     print(f'[stdout]\n{stdout.decode()}')
    # if stderr:
    #     print(f'[stderr]\n{stderr.decode()}')
    
    return proc.returncode, influxdb_timestamp



async def main() -> None:

    # await run_command('ping -I vrf0 10.0.1.11 -c 1')

    commands:list[Any] = [run_command('ping -I vrf0 10.0.1.1 -c 1 -w 1'),
                        run_command('ping -I vrf0 10.0.10.1 -c 1 -w 1'),
                        run_command('ping -I vrf0 10.0.11.1 -c 1 -w 1'),
                        run_command('ping -I vrf0 10.0.12.1 -c 1 -w 1'),
                        run_command('ping -I vrf0 10.0.13.1 -c 1 -w 1'),
                        run_command('ping -I vrf0 10.0.14.1 -c 1 -w 1'),
                        run_command('ping -I vrf0 10.0.15.1 -c 1 -w 1'),]
    
    result = await asyncio.gather(*commands)
    print(type(result))



if __name__ == '__main__':
    asyncio.run(main = main())        
