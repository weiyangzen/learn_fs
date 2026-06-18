# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/zblock.c

Purpose: Manages aligned byte buffers (`ZBlock`) and packet conversion.

Key behavior:
- `alloczblock` allocates one raw block containing aligned data, overflow sentinel bytes, and the `ZBlock` descriptor.
- `freezblock` verifies the overflow sentinel before freeing.
- `packet2zblock` copies packet bytes into a zblock.
- `zblock2packet` creates a packet from zblock bytes.
- `fmtzbinit` initializes a formatter to write into a zblock buffer.

Dependencies:
- Uses Plan 9 `Fmt`, packet APIs, and server allocation/error conventions.

Notable details:
- Sentinel size is 32 bytes and aborts on overwrite detection.
