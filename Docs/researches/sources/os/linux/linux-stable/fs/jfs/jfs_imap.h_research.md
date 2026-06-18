# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_imap.h

This header defines the JFS inode allocation map data structures, conversion macros, and exported imap/dinode management API.

Key responsibilities:
- Defines inode allocation group geometry: extents per IAG, summary-map sizes, inodes per extent relationships, maximum IAG count, and maximum allocation groups.
- Provides conversion macros from inode number to IAG number, IAG number to logical block number, and inode extent descriptor plus inode number to containing page block.
- Defines `struct iag`, the 4096-byte inode allocation group page containing AG links, free-list links, summary maps, working and persistent allocation maps, and inode extent descriptors.
- Defines on-disk and in-core per-AG controls for free inode lists, free extent lists, backed inode counts, and free inode counts.
- Defines the on-disk dinomap control page (`struct dinomap_disk`) and in-core map state (`struct dinomap`, `struct inomap`) with locks and atomic global counters.
- Declares public imap functions for mount/unmount, sync, read/write, special inode handling, allocation/free, persistent map updates, and extendfs rebuilds.

Important interactions:
- Included by inode allocation, inode commit, mount, and transaction code.
- Depends on transaction manager declarations because persistent map updates receive a `struct tblock`.
- Encodes the on-disk ABI for IAG pages and the inode map control page.

Notable invariants and risks:
- `struct iag` is exactly one 4096-byte page and includes large fixed arrays; layout changes would affect disk compatibility.
- `wmap` and `pmap` are separate 1-bit-per-inode maps with different lifecycle meanings.
- `inosmap` and `extsmap` summarize 32 inode extents per word and must remain consistent with the full maps and extent descriptors.
- `IAGTOLBLK()` reserves logical block 0 for the dinomap control page and starts IAG pages at block group `iagno + 1`.

Research notes:
- This header is the schema behind `jfs_imap.c`; understanding the map/list fields here is necessary to follow inode allocation and recovery behavior.
