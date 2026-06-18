# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast_checksum.h

`hast_checksum.h` declares the checksum pipeline API.

Key API:
- `checksum_name()` maps numeric checksum mode to a string.
- `checksum_send()` adds checksum metadata for outgoing data.
- `checksum_recv()` validates incoming data against checksum metadata.

The function signatures match the HAST protocol pipeline stage interface.
