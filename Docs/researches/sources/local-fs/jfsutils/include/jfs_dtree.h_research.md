# File Research: sources/local-fs/jfsutils/include/jfs_dtree.h

Defines JFS directory B+-tree entry and page formats.

Key contents:
- Defines directory entry data union `ddata_t`.
- Defines 32-byte `dtslot` segments for names.
- Defines internal directory entries `idtentry` with child `pxd_t`.
- Defines leaf directory entries `ldtentry` with inode number, name segment, and persistent directory-table index.
- Defines inline directory table slot format and helpers to store/extract 40-bit-ish leaf page addresses.
- Defines `dtroot_t`, the inline directory root embedded in `dinode`, including DASD limits, flags, parent inode, and sorted table.
- Defines `dtpage_t`, regular directory page layout with sibling links, flags, free list, self pxd, slots, and sorted table location.
- Defines page-size slot geometry constants and `DT_GETSTBL()` helper.
- Defines directory operation flags for create, lookup, remove, and rename.

Interactions:
- Embedded by `jfs_dinode.h`; processed by fsck directory tree routines declared in `xfsckint.h`.
- Uses `jfs_btree.h` flags and endian helpers.

Research notes:
- Supports legacy OS/2 directory entry length differences and newer persistent directory indexes.
