# File Research: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_helper.c

Read completely: 235 lines.

## Role

This file implements devfs clone bitmap helpers. The bitmap tracks available clone/unit numbers, where a clear bit means allocated and a set bit means free.

## Main Responsibilities

- Initialize and destroy bitmap storage:
  - `devfs_clone_bitmap_init()`
  - `devfs_clone_bitmap_uninit()`
- Grow bitmap storage with `devfs_clone_bitmap_extend()`.
- Find the first free unit with `devfs_clone_bitmap_fff()`.
- Test, allocate, free, and conditionally allocate units:
  - `devfs_clone_bitmap_chk()`
  - `devfs_clone_bitmap_set()`
  - `devfs_clone_bitmap_put()`
  - `devfs_clone_bitmap_get()`

## Synchronization and Lifetime Model

- A file-local recursive `devfs_bitmap_lock` protects structural bitmap integrity.
- Callers using check-then-set flows are still expected to hold their own higher-level lock to prevent semantic races.
- `devfs_clone_bitmap_get()` holds the bitmap lock and then calls `devfs_clone_bitmap_set()`, which is why the lock is recursive.
- `devfs_clone_bitmap_put()` first calls `devfs_config()` so pending devfs messages complete before a unit is made reusable.

## Important Interactions

- `devfs_core.c` uses this through `DEVFS_DEFINE_CLONE_BITMAP(ops_id)` to allocate compact IDs for `dev_ops` major-device encoding.
- Clone devices and device-op IDs rely on this helper not to reuse units before all pending devfs state has drained.

## Research Notes

- The bit representation is inverted relative to the public return values: bit set means free, `devfs_clone_bitmap_chk()` returns true when allocated.
- `devfs_clone_bitmap_get()` treats `unit > limit` as failure; if limits are meant to be inclusive this behavior is deliberate but worth noting.
- Growth adds two chunks when extending, reducing immediate repeat reallocations.
