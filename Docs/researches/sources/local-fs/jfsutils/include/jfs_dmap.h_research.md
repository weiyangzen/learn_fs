# File Research: sources/local-fs/jfsutils/include/jfs_dmap.h

Defines JFS block allocation map constants and on-disk structures.

Key contents:
- Constants for dmap tree sizes, leaf counts, blocks per dmap, dmapctl tree sizes, max allocation groups, map levels, and buddy values.
- Macros translate disk block numbers to dmap/L0/L1/control logical blocks and aggregate map size to top control level.
- Defines `struct dmaptree`, `struct dmap`, `struct dmapctl`, and `struct dbmap`.
- `struct dmap` is a 4096-byte page covering 8192 blocks with summary tree, working map, and persistent map.
- `struct dbmap` is a 4096-byte aggregate map descriptor with total map size, free counts, AG control fields, per-AG free table, AG size, and padding.

Interactions:
- Used by fsck block-map verification/rebuild, mkfs map initialization, and `libfs/diskmap.c`.
- `xfsck.h` embeds dmap/dmapctl/dbmap pointers in fsck block-map state.

Research notes:
- Encodes key allocator geometry; mistakes here affect all JFS allocation metadata interpretation.
