# File Research: sources/os/linux/linux-stable/fs/btrfs/props.c

This file implements Btrfs inode property handling backed by Btrfs xattrs. The current handler set contains one property, `btrfs.compression`, but the code is structured as a small extensible handler table.

Core structure:
- `struct prop_handler` defines:
  - xattr name
  - validation callback
  - apply callback
  - extract callback for inheritance
  - ignore callback
  - inheritable flag
- `prop_handlers_ht` is a hash table indexed by `btrfs_name_hash()` over the xattr name.
- `prop_handlers[]` currently registers `XATTR_BTRFS_PREFIX "compression"`.

Main public functions:
- `btrfs_props_init()` hashes and registers all property handlers at init time.
- `btrfs_validate_prop()` checks the xattr name has a valid Btrfs prefix, finds a handler, permits zero-length deletion, and otherwise calls the handler validator.
- `btrfs_ignore_prop()` asks the property handler whether this inode should ignore the property.
- `btrfs_set_prop()` writes or removes the backing xattr and applies the in-memory inode state. If applying a non-empty property fails after setting the xattr, it rolls the xattr back.
- `btrfs_load_inode_props()` scans xattr items for an inode and applies known Btrfs properties.
- `btrfs_inode_inherit_props()` copies inheritable properties from a parent directory inode to a new inode.

Property iteration:
- `iterate_object_props()` walks `BTRFS_XATTR_ITEM_KEY` items for an objectid, filters names under `XATTR_BTRFS_PREFIX`, matches known handlers using the hash bucket, copies name/value out of the extent buffer, and invokes a caller-supplied iterator.
- It dynamically resizes name and value buffers using `GFP_NOFS`.
- It releases the Btrfs path and frees buffers on exit.

Compression property behavior:
- `prop_compression_validate()` rejects compression on inodes that cannot compress, accepts valid compression types, and also accepts `no` and `none`.
- `prop_compression_apply()`:
  - zero length resets compression and no-compression flags.
  - `no`/`none` sets `BTRFS_INODE_NOCOMPRESS`, clears `BTRFS_INODE_COMPRESS`, and clears `prop_compress`.
  - `lzo`, `zlib`, and `zstd` set compression state; `lzo` and `zstd` also set their filesystem incompat feature bits.
- `prop_compression_ignore()` ignores compression xattrs for inode types other than regular files and directories.
- `prop_compression_extract()` returns the parent inode’s compression string only for active supported compression types.

Inheritance details:
- Inheritance only runs if the parent has `BTRFS_INODE_HAS_PROPS`.
- Each inheritable property is skipped if ignored for the child, absent on the parent, or invalid for the child.
- The current reservation logic assumes one supported property. If additional properties are added, the code has a reservation path using `btrfs_block_rsv_add()` for subsequent items.
- Successful inheritance writes the xattr, applies the in-memory property, and sets `BTRFS_INODE_HAS_PROPS`.

Role in the subsystem:
- Bridges user-visible Btrfs property xattrs and internal inode behavior, especially compression policy propagation from directories to new children.
