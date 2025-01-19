from dataclasses import dataclass, field

@dataclass
class Host:
   project: str = ''
   vlan: int = 0
   site: str = ''
   alias: str = ''
   ipv4addr: list[str] = field(default_factory=[])
   ipv4gw: str = ''
   ipv6addr: list[str] = field(default_factory=[])
   ipv6gw: str = ''
   pings: list[str] = field(default_factory=[])
