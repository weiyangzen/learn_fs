# File Research: sources/local-fs/btrfs-linux/fs/btrfs/props.c

This file implements Btrfs inode property handling through Btrfs xattrs, currently centered on the `btrfs.compression` property. It validates property names/values, applies properties to in-memory inode state, loads persisted properties from xattr items, and inherits selected properties from parent directories.

Core data model:
- `struct prop_handler` describes one property:
  - xattr name
  - validation callback
  - apply callback
  - extract callback for inheritance
  - ignore callback
  - inheritable flag
- `prop_handlers_ht` is a hash table keyed by Btrfs name hash for quick xattr-property lookup.

Primary exported functions:
- `btrfs_props_init()` registers static property handlers in the hash table.
- `btrfs_validate_prop()` validates that a named property exists and that the value is accepted.
- `btrfs_ignore_prop()` asks whether a valid property should be skipped for a target inode.
- `btrfs_set_prop()` writes/removes the xattr and applies the resulting in-memory state.
- `btrfs_load_inode_props()` scans an inode’s xattr items and applies recognized properties.
- `btrfs_inode_inherit_props()` copies inheritable properties from parent to newly created inode.

Property lookup and scanning:
- `find_prop_handlers_by_hash()` selects the handler bucket from `prop_handlers_ht`.
- `find_prop_handler()` matches exact xattr names inside a bucket.
- `iterate_object_props()` walks xattr items for an object ID, filters names with `XATTR_BTRFS_PREFIX`, copies name/value data out of extent buffers, and invokes an iterator callback for recognized properties.
- `inode_prop_iterator()` applies properties during inode load and sets `BTRFS_INODE_HAS_PROPS` on success.

Compression property:
- Registered xattr name is `XATTR_BTRFS_PREFIX "compression"`.
- `prop_compression_validate()` requires a compressible inode and accepts known compression types plus `"no"` and `"none"`.
- `prop_compression_apply()` updates inode flags:
  - zero-length value resets compression/nocompression state.
  - `"no"`/`"none"` sets `BTRFS_INODE_NOCOMPRESS`.
  - `"lzo"`, `"zlib"`, and `"zstd"` set `BTRFS_INODE_COMPRESS` and `prop_compress`.
  - LZO and ZSTD also set the corresponding incompat feature flags.
- `prop_compression_ignore()` skips non-regular and non-directory inodes.
- `prop_compression_extract()` converts the parent’s compression enum back to a property string for inheritance.

Error handling and consistency:
- `btrfs_set_prop()` rolls back the xattr if applying a non-empty property fails.
- Removing a property applies the handler with `NULL, 0` and asserts success.
- Inheritance validates extracted parent values before propagation.
- `btrfs_inode_inherit_props()` accounts for the current single-property reservation assumption and reserves extra metadata only after the first property if more are added later.

Dependencies:
- Uses xattr helpers from `xattr.h`.
- Uses compression helpers from `compression.h`.
- Uses Btrfs dir-item accessors to parse packed xattr items from leaves.
- Uses inode runtime flags from `btrfs_inode.h`.
