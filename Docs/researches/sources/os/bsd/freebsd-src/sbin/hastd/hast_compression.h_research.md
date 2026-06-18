# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast_compression.h

`hast_compression.h` declares the compression pipeline API.

Key API:
- `compression_name()` maps numeric compression mode to a string.
- `compression_send()` optionally compresses outgoing data and annotates nv metadata.
- `compression_recv()` decompresses incoming data based on nv metadata.

The function signatures are compatible with the HAST protocol pipeline stage table.
