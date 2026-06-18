# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/write.c

Purpose: Client utility to write one data block from stdin to a Venti server.

Key behavior:
- Reads up to `VtMaxLumpSize+1`, rejects oversized input, connects to a server, optionally zero-truncates the block, writes it with selected Venti type, prints the returned score, and exits.
- Supports `-h host`, `-t type`, and `-z`.

Dependencies:
- Uses libventi connection/write APIs and score formatting.

Notable details:
- Defaults block type to `VtDataType`.
