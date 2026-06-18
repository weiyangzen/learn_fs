# File Research: sources/local-fs/jfsutils/include/jfs_imap.h

Defines JFS inode allocation map structures.

Key contents:
- Constants for inode allocation groups, extents per IAG, summary maps, pages per inode extent, max IAGs, and allocation-map byte sizes.
- Macros convert inode number to IAG, IAG to logical block, and inode number/PXD to inode page block.
- Defines 4096-byte `struct iag` with AG start, IAG number, inode/extent free-list links, summary maps, free counts, working/persistent allocation maps, and inode extent PXD array.
- Defines per-AG `struct iagctl`.
- Defines 4096-byte `struct dinomap` inode-map control page with global free counts, inode extent block geometry, and per-AG control table.

Interactions:
- Used by fsck inode map verification/rebuild and by inode allocation tooling.

Research notes:
- IAG layout combines allocation bitmaps and extent address table in one page, making endian/layout correctness central.
