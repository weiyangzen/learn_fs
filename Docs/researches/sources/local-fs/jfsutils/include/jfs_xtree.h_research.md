# File Research: sources/local-fs/jfsutils/include/jfs_xtree.h

Defines JFS extent allocation descriptor tree structures.

Key contents:
- Includes `jfs_btree.h`.
- Defines `xad_t`, a 16-byte extent descriptor with flags, split 40-bit file offset, 24-bit length, and split disk address.
- Provides XAD set/get macros for offset, address, and length.
- Defines XAD flags: new, extended, compressed, not recorded, copy-on-write.
- Defines xtree slot geometry and root/page max entry constants.
- Defines `xtpage_t`, a 4096-byte union containing xtree header or XAD array.

Interactions:
- Embedded in dinodes and used by fsck xTree processing.
- Used by log manager record payloads and allocation map updates.

Research notes:
- Supports COW flag in the on-disk extent descriptor even though jfsutils is primarily repair/utility code.
