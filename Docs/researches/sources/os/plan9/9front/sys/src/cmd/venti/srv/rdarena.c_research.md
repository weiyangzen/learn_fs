# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/rdarena.c

`rdarena` copies a named arena from an arena partition to standard output. It loads the partition, finds the arena by name, and writes the arena’s header, data/directory region, and tail in block-aligned chunks.

Flags allow quiet output and verbose arena-part printing. The copy range starts one block before `arena->base` and extends through the tail block, matching the standalone arena image format consumed by other tools.

This is a backup/extraction utility for moving individual arenas without copying an entire arena partition.
