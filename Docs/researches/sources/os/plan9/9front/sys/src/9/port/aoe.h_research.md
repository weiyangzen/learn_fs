# File Research: sources/os/plan9/9front/sys/src/9/port/aoe.h

ATA over Ethernet protocol definitions shared by AoE code.

Key contents:
- AoE command enums for ATA, config, mask, and reserve/release operations.
- Config command values and mask/reservation directive and error codes.
- AoE EtherType, sector size, maximum config length, structure sizes, version, flags, and ATA flags.
- Wire-format structs:
  - `Aoehdr`: Ethernet + AoE header.
  - `Aoeata`: ATA command payload.
  - `Aoecfg`: config payload.
  - `Aoemd`: mask directive entry.
  - `Aoem`: mask command header.
  - `Aoerr`: error response with flexible Ethernet address list.
- External error strings `Echange` and `Enotup`.

Notable dependencies:
- `Eaddrlen` from network headers.

Research notes:
- Structures are byte-array wire formats rather than host-endian integer structs, which avoids alignment/endian assumptions in the header itself.
