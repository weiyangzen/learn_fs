# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/disk.h

This header defines the `Disk` object and disk-allocation API for `cfs`.

Key contents:
- `Disk` embeds `Bcache` and adds total block count, allocation block count, bitmap bits per allocation block, pointers per indirect block, and cache name.
- Prototypes for disk initialization, formatting, data block allocation, pointer block allocation, and freeing.
- External `debug` and `DPRINT` macro.

Filesystem relevance:
- Direct. Declares the disk allocation layer for the `cfs` cache filesystem.
