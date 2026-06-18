# File Research: sources/os/linux/linux-stable/fs/isofs/isofs.h

Private ISOFS header defining core in-memory structures, helpers, and cross-file declarations.

Key definitions:
- `enum isofs_file_format`: normal, sparse, compressed.
- `struct iso_inode_info`: iget block/offset identity, first extent, format parameters, Level 3 next-section links, section size, embedded VFS inode.
- `struct isofs_sb_info`: volume counts, zone size, Rock Ridge/Joliet/name mapping state, mount flags, modes, uid/gid, NLS table.
- Numeric helpers `isonum_711` through `isonum_733` parse ISO little/big/both-endian fields, intentionally trusting little-endian for broken mastering tools in 723/733.
- `isofs_get_ino()` derives a convenient inode number from block and offset.
- `isofs_normalize_block_and_offset()` normalizes directory identities to their `.` entry for dcache and NFS export consistency.

Also declares Rock Ridge, Joliet, lookup, bread/get_blocks, iget, directory ops, symlink aops, and export ops.
