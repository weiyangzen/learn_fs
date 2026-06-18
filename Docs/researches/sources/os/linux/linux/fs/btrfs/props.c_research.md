# File Research: sources/os/linux/linux/fs/btrfs/props.c

This file implements Btrfs inode properties backed by Btrfs xattrs. The current registered property is `btrfs.compression`.

Core model:
- `struct prop_handler` describes one property: xattr name, validate/apply/extract/ignore callbacks, and inheritance flag.
- `prop_handlers_ht` is a hash table keyed by Btrfs name hash for xattr-property lookup.

Primary exported functions:
- `btrfs_props_init()` registers static handlers.
- `btrfs_validate_prop()` checks property name and value.
- `btrfs_ignore_prop()` asks whether a valid property should be skipped for an inode.
- `btrfs_set_prop()` writes/removes the xattr and applies the in-memory inode state.
- `btrfs_load_inode_props()` scans an inode’s xattr items and applies known properties.
- `btrfs_inode_inherit_props()` copies inheritable properties from a parent directory to a new inode.

Property scanning:
- `iterate_object_props()` walks xattr items for an object ID, filters names under `XATTR_BTRFS_PREFIX`, copies name/value data from extent buffers, finds matching handlers, and invokes a callback.
- `inode_prop_iterator()` applies persisted properties and sets `BTRFS_INODE_HAS_PROPS` on success.

Compression property:
- `prop_compression_validate()` requires a compressible inode and accepts known compression types plus `no` and `none`.
- `prop_compression_apply()` clears state for zero-length values, sets `BTRFS_INODE_NOCOMPRESS` for `no`/`none`, or sets `BTRFS_INODE_COMPRESS` and `prop_compress` for `lzo`, `zlib`, or `zstd`.
- LZO and ZSTD set their filesystem incompat feature bits.
- `prop_compression_ignore()` skips non-regular and non-directory inodes.
- `prop_compression_extract()` converts parent compression state back to a string for inheritance.

Consistency notes:
- `btrfs_set_prop()` rolls back the xattr if applying a non-empty property fails.
- Property removal applies the handler with `NULL, 0` and asserts success.
- Inheritance validates extracted parent values before propagation.
- Current metadata reservation comments assume only one supported property.

Dependencies:
- Uses xattr helpers, dir-item accessors, compression helpers, transaction metadata reservations, and inode runtime flags.
