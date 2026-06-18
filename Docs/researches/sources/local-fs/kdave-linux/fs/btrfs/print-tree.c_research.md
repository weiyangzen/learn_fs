# File Research: sources/local-fs/kdave-linux/fs/btrfs/print-tree.c

## Purpose

Diagnostic Btrfs tree printer for kernel logs. It formats root names, key types, leaves, internal nodes, and selected item payloads so developers can inspect B-tree metadata during debugging.

## Main Interfaces

- `btrfs_root_name(const struct btrfs_key *key, char *buf)`: returns a symbolic root name for known root objectids, formats tree reloc roots with offset, otherwise returns numeric objectid text.
- `btrfs_print_leaf(const struct extent_buffer *l)`: logs a leaf header and each item’s key, offset, size, and type-specific payload.
- `btrfs_print_tree(const struct extent_buffer *c, bool follow)`: logs an internal node or leaf. If `follow` is true, recursively reads and prints children.

## Internal Behavior

- Maintains `root_map[]` for well-known roots including root, extent, chunk, device, checksum, quota, UUID, free-space, block-group, raid-stripe, and remap trees.
- `key_type_string()` maps Btrfs item key types to readable labels, including newer entries such as:
  - `BTRFS_EXTENT_OWNER_REF_KEY`
  - `BTRFS_RAID_STRIPE_KEY`
  - `BTRFS_REMAP_KEY`
  - `BTRFS_REMAP_BACKREF_KEY`
- Leaf printing handles many item classes:
  - inode items and timestamps
  - inode refs and extrefs
  - dir items, dir indexes, xattrs
  - root items
  - extent and metadata items with inline refs
  - file extents, including inline extents
  - block group, chunk, device, and device extent items
  - UUID items
  - raid stripe items
  - remap items
- Extent item printing validates minimum item size, prints tree block info when present, iterates inline refs, and warns about misaligned shared parents.
- Simple quota owner refs are printed through `print_extent_owner_ref()` and assert the `SIMPLE_QUOTA` incompat feature.
- `print_eb_refs_lock()` logs extent-buffer reference and lock-owner state only under `CONFIG_BTRFS_DEBUG`.
- Recursive tree following uses `read_tree_block()` with `btrfs_tree_parent_check` populated from the parent pointer generation, owner root, and first key.

## Dependencies

Uses Btrfs accessor helpers and tree structures from `ctree.h`, `accessors.h`, `file-item.h`, `tree-checker.h`, `volumes.h`, and `raid-stripe-tree.h`.

## Error Handling and Safety Notes

- Null extent buffers are ignored.
- Unexpected extent item sizes are logged and skipped.
- UUID item sizes must be aligned to `sizeof(u64)`.
- Recursive tree traversal uses `BUG()` if a child has an impossible level relationship after read.
- Unknown item key types are still printed as `UNKNOWN.<type>`.

## Role in the System

This file is not part of normal filesystem semantics; it is a debugging aid used to inspect on-disk metadata in kernel logs.
