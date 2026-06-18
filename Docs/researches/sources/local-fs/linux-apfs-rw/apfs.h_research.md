# File Research: sources/local-fs/linux-apfs-rw/apfs.h

This is the central private header for the APFS kernel module. It includes Linux kernel headers, `apfs_raw.h`, compatibility wrappers, in-memory APFS data structures, inline helpers, logging/assertion macros, and cross-file function declarations.

Compatibility coverage is broad. It handles RHEL-specific version tests, pre-4.14 superblock flag names, pre-5.3 lockdep helpers, `submit_bh()` API differences, newer `fileattr` naming, inode state accessors for newer kernels, `read_folio`/`readpage` era APIs through declarations, and block-device handle/file mode differences.

Major in-memory structures:
- `struct apfs_object`: generic APFS object wrapper with superblock, block number, object id, buffer head, raw data pointer, and ephemeral flag.
- `struct apfs_node`: in-memory b-tree node metadata, table/free/key/value offsets, free-list lengths, and backing `apfs_object`.
- `struct apfs_spaceman`: in-memory space manager, chunk geometry, free counts, free-cache range, internal-pool bitmap metadata.
- `struct apfs_nx_transaction`: shared container transaction state, delayed commit work, joined inodes/buffers, and transaction counters.
- `struct apfs_blkdev_info`: portability wrapper for block device state, including newer kernel handles/files and optional Fusion tier path.
- `struct apfs_nxsb_info`: container-wide state: devices, raw container superblock, xid, ephemeral list, mounted volume list, spaceman, transaction, and `nx_big_sem`.
- `struct apfs_omap` and cache types: object-map root, small direct-mapped omap cache, latest snapshot xid, and refcount.
- `struct apfs_sb_info`: per-volume state, including catalog root, omap, mounted snapshot metadata, mount options, default crypto state, private directory, and orphan cleanup work.
- `struct apfs_query`: b-tree query state with key, parent chain, flags, found key/value offsets, and recursion depth.
- `struct apfs_dstream_info`: file/xattr data stream state, cached extent, sparse byte count, dirty flag, and sharing state.
- `struct apfs_inode_info`: APFS inode extension with 64-bit inode id, parent id, creation time, APFS flags, optional dstream, cleanup state, and embedded VFS inode.

Important inline helpers:
- Node predicates: leaf/root/fixed key-value size.
- Superblock accessors: `APFS_SB`, `APFS_NXI`, `APFS_SM`.
- Volume predicates: sealed, encrypted, case-insensitive, normalization-insensitive.
- Key initializers for omap, free queue, extents, inode, file extents, dstream id, crypto state, sibling links/maps, xattrs, snapshots.
- Catalog key header helpers: `apfs_key_set_hdr`, `apfs_cat_type`, `apfs_cat_cnid`.
- Query storage selection for physical, virtual, and ephemeral b-trees.
- 64-bit inode helpers `apfs_ino` and `apfs_set_ino`.
- Buffer-head mapping/read/get helpers that route APFS block numbers to the main or Fusion tier-2 device.

The file declares the module’s internal API across `btree.c`, `compress.c`, `dir.c`, `extents.c`, `file.c`, `inode.c`, `key.c`, `node.c`, `object.c`, `snapshot.c`, `spaceman.c`, `super.c`, `transaction.c`, `xattr.c`, and `xfield.c`.

Research relevance: this header is the contract tying the driver together. It defines the shared locking model, object/query abstractions, APFS metadata state, VFS operation declarations, and block-device mapping policy.
