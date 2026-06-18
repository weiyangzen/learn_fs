# File Research: sources/os/linux/linux-stable/fs/btrfs/free-space-tree.h

## Purpose

Declares the public interface for the Btrfs free-space tree feature implemented in `free-space-tree.c`.

## Constants

`BTRFS_FREE_SPACE_BITMAP_SIZE` is 256 bytes for newly created bitmap items, and `BTRFS_FREE_SPACE_BITMAP_BITS` is the number of sectors represented by that default bitmap. The header notes that existing bitmap items may be smaller, especially the last bitmap in a block group.

## Public API Surface

The header exposes threshold calculation, free-space tree create/delete/rebuild, runtime loading, block-group add/remove hooks, transactional range add/remove hooks, orphan-entry cleanup, info-item lookup, and root lookup.

## Test-Only API

With Btrfs sanity tests enabled, the header exposes internal add/remove helpers, conversion helpers, and bitmap bit testing. This allows unit-style tests to exercise extent/bitmap tree behavior without going through all normal mount or allocation paths.
