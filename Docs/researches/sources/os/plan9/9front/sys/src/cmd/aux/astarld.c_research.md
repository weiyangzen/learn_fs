# File Research: sources/os/plan9/9front/sys/src/cmd/aux/astarld.c

Role: Loader for Astar device memory via `#G/astarNctl` and `#G/astarNmem`.

Main behavior:
- Supports unit selection `-0`..`-3`, dump mode, raw image mode, no-load test mode, and no-start mode.
- In normal mode, opens the selected control and memory files, writes `download`, loads data, and optionally writes `run`.
- In no-load mode, writes to `/tmp/astarmem`.

Input formats:
- Raw image mode copies bytes directly into memory.
- Default mode parses Intel HEX records with `rdcpline`, verifies checksums, applies extended segment records, checks address range against 64 KiB memory, writes data, and reads back for verification.

Important helpers:
- `clearmem` zeroes the target memory file and verifies by reading back.
- `hex` and `rdcpline` implement the Intel HEX decoder.

Failure behavior:
- Uses `sysfatal` on malformed records, out-of-range addresses, I/O failures, or checksum errors.
