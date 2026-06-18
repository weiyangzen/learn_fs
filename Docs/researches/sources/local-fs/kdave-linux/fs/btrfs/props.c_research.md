# File Research: sources/local-fs/kdave-linux/fs/btrfs/props.c

## Purpose

Implements Btrfs inode property handling backed by Btrfs xattrs. The current property table supports `btrfs.compression`.

## Core Structures

- `struct prop_handler`: handler record for a property:
  - xattr name
  - validation callback
  - apply callback
  - extraction callback for inheritance
  - ignore callback
  - inheritable flag
- `prop_handlers_ht`: hash table keyed by `btrfs_name_hash()` of the xattr name.

## Main Interfaces

- `btrfs_props_init()`: registers property handlers in the hash table.
- `btrfs_validate_prop()`: validates a property name and optional value.
- `btrfs_ignore_prop()`: asks the handler whether the property should be skipped for an inode.
- `btrfs_set_prop()`: writes/removes the xattr and applies the in-memory inode state.
- `btrfs_load_inode_props()`: scans an inode’s xattr items and applies known Btrfs properties.
- `btrfs_inode_inherit_props()`: propagates inheritable properties from parent to new inode.

## Property Scanning

`iterate_object_props()` walks `BTRFS_XATTR_ITEM_KEY` items for an objectid, filters for `XATTR_BTRFS_PREFIX`, matches registered handlers, reads values from the leaf into temporary buffers, and invokes a supplied iterator callback.

## Compression Property

The only registered handler is `btrfs.compression`.

Validation:
- Rejects inodes that cannot be compressed.
- Accepts valid compression strings from `btrfs_compress_is_valid_type()`.
- Also accepts `no` and `none`.

Apply behavior:
- Empty value clears compression and no-compression flags.
- `no` or `none` sets `BTRFS_INODE_NOCOMPRESS`.
- `lzo`, `zlib`, and `zstd` set `BTRFS_INODE_COMPRESS` and `inode->prop_compress`.
- LZO and ZSTD set corresponding filesystem incompat feature bits.

Ignore behavior:
- Compression xattr is ignored for non-regular-file and non-directory inodes.

Inheritance:
- Only inheritable handlers are considered.
- Parent value is extracted from in-memory inode state.
- The child is validated before xattr insertion.
- The code assumes one currently supported property for reservation purposes, with a note that more properties would require revisiting metadata reservation.

## Error Handling

- Unknown or malformed property names return `-EINVAL`.
- Allocation failures while scanning xattrs return `-ENOMEM`.
- If applying a just-written xattr fails, `btrfs_set_prop()` removes the xattr again.
- Load-time apply failures are warned but do not abort the whole load.

## Role in the System

This file bridges persistent Btrfs property xattrs and runtime inode flags, especially for compression policy and inheritance.
