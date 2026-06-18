# File Research: sources/os/plan9/9front/sys/src/cmd/crc32.c

Configurable CRC-32 calculator. It builds a 256-entry table from a polynomial and computes checksums over stdin or named files.

Important behavior:
- Defaults: reflected CRC polynomial `0xedb88320`, initial value 0, final xor `-1`.
- Options: `-x xorval`, `-i initial`, `-p poly`.
- `sum()` streams data in `IOUNIT` chunks and prints either just the CRC or `CRC<TAB>filename`.
- Read/open failures set the process exit string but processing continues for later files.
