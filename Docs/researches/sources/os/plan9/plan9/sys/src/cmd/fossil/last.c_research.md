# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/last.c

Standalone helper that prints the last archived Venti root score from a fossil disk.

It reads the fossil header magic and block size at fixed offsets, locates the superblock, reads the 20-byte `last` score field, and prints it as `vac:<hex>`. It performs direct byte parsing rather than using the full fossil packing layer.
