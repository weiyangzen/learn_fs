# File Research: sources/os/linux/linux/fs/befs/btree.h

## Purpose
Public BeFS B+tree API header.

## Interfaces
- `befs_btree_find()`: exact key lookup in a BeFS datastream-backed B+tree.
- `befs_btree_read()`: ordinal read/traversal of B+tree leaf entries, returning key, key size, and value.

## Research Notes
This small header exposes only the two operations needed by the VFS directory implementation: name lookup and directory iteration.
