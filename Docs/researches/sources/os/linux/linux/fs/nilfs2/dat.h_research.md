# File Research: sources/os/linux/linux/fs/nilfs2/dat.h

This header declares the DAT API for virtual-to-physical block translation and virtual block lifecycle management.

Declared capabilities:
- Translate a virtual block number to a physical sector.
- Prepare/commit/abort allocation, start, end, and update transitions.
- Mark DAT entries dirty.
- Free virtual block numbers.
- Move a virtual block to a new physical block.
- Export virtual block info to callers.
- Read or get the DAT metadata inode.

Important role:
- Bmap implementations use this interface to support virtual block number mode.
- GC and ioctl code use it to inspect, move, and free virtual blocks.
- Metadata initialization uses it to create the DAT inode with allocator and shadow-map support.
