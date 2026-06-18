# File Research: sources/local-fs/xfsprogs/repair/da_util.h

## Purpose

`da_util.h` declares shared cursor structures and helper functions for directory/attribute DA btree traversal and validation in repair.

## Main Types

- `struct da_level_state` stores one DA tree level’s buffer, file block number, hash value, entry index, and dirty state.
- `da_bt_cursor_t` stores active depth, inode number, greatest DA block number seen, dinode pointer, per-level states, and the fork block map.

## Public API

The header declares DA block reading, cursor release, interior traversal, regular path verification, and final right-edge verification functions.

## Important Invariants

- `level` has `XFS_DA_NODE_MAXDEPTH` entries.
- `blkmap` must map DA file blocks to filesystem blocks before traversal.
- The same helpers serve directory and attribute forks, selected by `whichfork`.

## Research Notes

This header captures repair’s local model of a DA btree cursor. It is intentionally independent of libxfs runtime cursors because repair needs salvage reads and custom validation/repair behavior.
