# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_all.c

## Purpose

`ctfs_all.c` implements the `/system/contract/all` synthetic directory, which presents all visible contracts in a zone as numeric symlink entries.

## File Shape

- Size: 157 lines, 3,941 bytes.
- SHA-256: `764fbab06e5731b0bb4371c698877876ca1ac606c1ce8ab0c0d94858f49ac35d`.
- Public creator: `ctfs_create_adirnode()`.
- Operation vector: `ctfs_tops_adir`.

## Core Behavior

- `ctfs_create_adirnode()` creates a GFS dynamic directory with custom readdir and lookup callbacks.
- `ctfs_adir_getattr()` reports a read-only directory whose size is `2 + total contracts across all contract types`; timestamps are based on the filesystem mount time.
- `ctfs_adir_do_lookup()` parses the lookup name as a numeric contract ID, verifies no trailing characters, looks up the contract in the caller's zone, and returns a symlink vnode created by `ctfs_create_symnode()`.
- `ctfs_adir_do_readdir()` uses `contract_lookup()` beginning at the current offset in the vnode's zone, emits the next contract ID as both name and inode-derived symlink target entry, and advances the offset.

## Dependencies And Contracts

- Uses GFS directory helpers, contract global lookup/count APIs, and CTFS inode macros.
- Only contracts visible in `VTOZONE(vp)->zone_uniqid` are exposed.

## Maintenance Notes

The directory is dynamically generated and not cached by a static dirent table. Numeric name parsing uses `stoi()` and requires the full name to be numeric.
