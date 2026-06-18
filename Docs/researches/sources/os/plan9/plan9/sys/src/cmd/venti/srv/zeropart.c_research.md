# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/zeropart.c

Purpose: Zeros most of a Venti partition/device.

Key behavior:
- Allocates a zeroed `MaxIoSize` zblock and writes zeros from `PartBlank` to the partition end in large chunks, then block-size chunks.
- Flushes the partition and frees the zblock.

Dependencies:
- Uses `writepart`, `flushpart`, and `alloczblock`.

Notable details:
- Starts at `PartBlank`, preserving the initial partition area before that offset.
