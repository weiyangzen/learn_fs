# File Research: sources/local-fs/linux-apfs-rw/apfs_raw.h

This header defines packed APFS on-disk data structures, constants, flags, masks, and record formats. It is the driver’s local APFS disk-format specification.

It starts with object identifiers, object type masks, storage flags, APFS object types, and `struct apfs_obj_phys`, the common on-disk object header containing checksum, oid, xid, type, and subtype.

Object-map definitions include omap flags, `struct apfs_omap_phys`, omap value flags, `struct apfs_omap_val`, and snapshot omap records. These feed object-id to block-number resolution in `btree.c` and object loading elsewhere.

B-tree definitions cover node flags, key/value location structs, `struct apfs_btree_node_phys`, b-tree info flags, fixed b-tree info, and root b-tree info counters. These are consumed by node and btree logic for searching, insertion, splitting, replacement, and metadata count updates.

Catalog and file metadata definitions include:
- Directory record values and dentry key formats, both hashed and unhashed.
- Physical extent values, kind masks, file extent values, and file extent flags.
- Dstream id values and crypto state records.
- APFS inode numbers, inode internal flags, BSD flags, and `struct apfs_inode_val`.
- Extended field blob/key format and xfield type constants.
- Dstream, directory stats, sibling link, and sibling map values.
- Catalog record type enum and key header format.

Space management definitions include chunk info records, chunk info blocks, chunk info address blocks, free queue structures, device allocation info, allocation zone data, internal-pool bitmap constants, and `struct apfs_spaceman_phys`.

Container-level definitions include NX magic, limits, feature flags, incompatibility masks, block-size limits, counter indices, `struct apfs_nx_superblock`, checkpoint mapping records, and checkpoint map blocks.

Volume-level definitions include volume magic, flags, roles, supported feature masks, incompatible feature masks, modified-by history, protection classes, crypto identifiers, wrapped metadata crypto state, and `struct apfs_superblock`.

Extended attributes and sealed-volume definitions include xattr names, xattr value/dstream formats, integrity metadata, hash algorithm constants, file extent tree key/value formats, file info records, sealed catalog index value format, and compressed file formats.

Compression definitions enumerate APFS decmpfs algorithms: zlib, LZVN, plain, LZFSE, and lzbitmap, in both attribute and resource-fork storage forms. Snapshot metadata/name records and keybag/locker formats are also defined.

Research relevance: this file is purely structural but critical. It establishes exact byte layouts and masks for every higher-level operation in the implementation files.
