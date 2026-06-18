# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sharefs/sharetab.c

## Purpose

`sharetab.c` maintains the per-zone in-kernel share table behind `sharefs` and implements the `sharefs` syscall operations for adding, replacing, and removing share records.

## Main Interfaces

Public entry points are `sharefs_sharetab_init()`, `sharetab_get_globals()`, `sharefs_impl()`, and `sharefs()`. Internal helpers include `sharefree()`, `sharefs_add()`, `sharefs_remove()`, `sharetab_zone_init()`, and `sharetab_zone_fini()`.

The syscall accepts `enum sharefs_sys_op` values such as `SHAREFS_ADD`, `SHAREFS_REPLACE`, and `SHAREFS_REMOVE` plus a user `share_t` with string fields.

## Behavior And Data Flow

Per-zone state is allocated by `sharetab_zone_init()` and attached with `zone_key_create()`. Each zone gets `sharetab_lock`, `sharefs_lock`, share count, aggregate text size, generation number, mtime, snap time, and a linked list of per-filesystem share hash tables.

`sharefs_impl()` first checks whether remove/replace can possibly succeed, copies in the user `share_t`, allocates a temporary copy buffer sized by `iMaxLen`, copies mandatory `path` and `fstype` strings, then copies `res`, `opts`, and `descr` for add/replace. The `SHARETAB_COPYIN` macro allocates kernel strings, records lengths in `sharefs_lens_t`, and contributes to `sh_size`.

`sharefs_add()` finds or creates the per-fstype share table, computes the hash bucket from path, computes exported text size including separators and newline, replaces an existing exact path match or inserts a new share at the bucket head, updates bucket/table/global counts, updates aggregate size, mtime, and generation, and frees replaced entries.

`sharefs_remove()` finds the matching fstype and exact path entry, unlinks it from the hash bucket, decrements counts, subtracts size, updates mtime and generation, frees both the stored share and the caller's temporary share, and returns `ENOENT` when no match exists.

`sharetab_zone_fini()` destroys locks and walks every fstype table and bucket, freeing all shares, fstype strings, table nodes, and the per-zone globals.

## Security And Zones

`sharefs()` enforces privileges before calling `sharefs_impl()`: global-zone callers require `secpolicy_sys_config()`, while non-global zones use `secpolicy_nfs()` to match existing ZFS share policy behavior. All state lookup uses `sharetab_get_globals(curzone)` or the mount zone.

## Dependencies

The file depends on zone-specific storage, kernel memory allocation, `copyin()`/`copyinstr()`, policy checks, atomic counters, high-resolution timestamps, the `pkp_tab_hash()` hash function, and sharefs structures from `sharefs/sharefs.h`.

## Research Notes

This file is the mutation side of the sharefs snapshot model. Important audit points are trusting `iMaxLen` for copy buffer sizing, path-length comparisons that mix copied length and `strlen()`, `sharetab_size` accounting used by `sharefs_snap_create()`, generation increments, and privilege behavior in non-global zones.
