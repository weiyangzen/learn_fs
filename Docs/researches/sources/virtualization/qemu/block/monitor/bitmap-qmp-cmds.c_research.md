# File Research: sources/virtualization/qemu/block/monitor/bitmap-qmp-cmds.c

## Purpose
Implements QMP commands and shared helpers for QEMU block dirty bitmap management.

## Main Entry Points
- `block_dirty_bitmap_lookup()` validates node and bitmap names, locates the `BlockDriverState`, and returns the named bitmap.
- `qmp_block_dirty_bitmap_add()` creates a transient or persistent dirty bitmap with validated/default granularity and optional disabled state.
- `block_dirty_bitmap_remove()` checks busy/read-only state, removes persistent bitmap metadata when needed, and optionally releases the bitmap.
- `qmp_block_dirty_bitmap_remove()`, `qmp_block_dirty_bitmap_clear()`, `qmp_block_dirty_bitmap_enable()`, and `qmp_block_dirty_bitmap_disable()` expose simple QMP operations.
- `block_dirty_bitmap_merge()` merges local or external source bitmaps into a destination bitmap with rollback backup support.
- `qmp_block_dirty_bitmap_merge()` exposes merge through QMP.

## Internal Mechanics
The file is a thin validation and orchestration layer over the dirty-bitmap subsystem. It normalizes common lookup errors, enforces bitmap name/granularity rules, checks bitmap state flags before mutating, and handles persistent bitmap storage separately from in-memory release. Merge supports a list containing either local bitmap names on the destination node or external `{ node, name }` references. The first merge can create an `HBitmap` backup, and failures restore the destination from that backup.

## Dependencies
Uses QEMU block dirty bitmap APIs, block node lookup, QAPI-generated block command types, `HBitmap`, `QDict`/QAPI variant types, and QEMU error reporting.

## Risks and Notes
The merge rollback backup is only created once and reused for the whole batch, so the function treats the requested merge list as an atomic operation from the destination bitmap’s perspective. Persistent remove can fail before the in-memory bitmap is released, preserving metadata consistency. Bitmap operations rely on `bdrv_dirty_bitmap_check()` flag policies, so busy/read-only behavior is centralized in the block layer rather than reimplemented here.
