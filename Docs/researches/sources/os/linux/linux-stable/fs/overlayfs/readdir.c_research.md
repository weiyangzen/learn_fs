# File Research: sources/os/linux/linux-stable/fs/overlayfs/readdir.c

## Purpose

`readdir.c` implements overlayfs directory iteration. It builds merged directory views from upper/lower layers, suppresses hidden entries via whiteouts, handles xwhiteouts, maintains per-directory read caches, adjusts exposed inode numbers, supports direct real-dir iteration when possible, and cleans work/index directories.

## Main Types

- `struct ovl_cache_entry`: one directory entry in a merged cache, with original and casefolded names, real and exposed inode numbers, d_type, upper/whiteout/xwhiteout flags, list node, and rb-tree node.
- `struct ovl_dir_cache`: cached merged entries plus version and refcount.
- `struct ovl_readdir_data`: temporary state for reading real dirs into overlay cache structures.
- `struct ovl_dir_file`: per-open directory file state, including whether iteration can use a real dir directly, cached upperfile, merged cache, and cursor.

## Directory Cache Flow

For merged directories, `ovl_cache_get()` returns a valid cache if the inode version matches. Otherwise it allocates a cache and calls `ovl_dir_read_merged()`.

`ovl_dir_read_merged()` iterates overlay paths from upper through lower layers using `ovl_path_next()`. Upper and intermediate layers insert into an rb-tree to suppress duplicates. The lowest layer is inserted ahead of upper entries to keep offsets more stable.

Whiteouts are filtered through two mechanisms:

- Character-device whiteouts are tracked as possible whiteouts and later checked with `ovl_check_whiteouts()`.
- xwhiteouts are checked lazily for regular zero-sized files in directories marked by `overlay.opaque=x`.

Casefold-enabled overlays use `utf8_casefold()` and compare casefolded names in the rb-tree.

## Iteration Paths

`ovl_iterate()` chooses among three paths:

- `ovl_iterate_merged()` for merge dirs or dirs with whiteouts.
- `ovl_iterate_real()` for direct real-dir iteration with inode-number translation where needed.
- Direct `iterate_dir()` on the real file when no adjustment is needed.

`ovl_dir_is_real()` allows direct iteration only when the overlay inode does not have `OVL_WHITEOUTS`.

`ovl_dir_reset()` invalidates a per-open cache if the overlay inode version changed, and transitions from real to merged iteration if a directory was copied up.

## Inode Number Handling

`ovl_cache_update()` resolves deferred inode numbers for upper entries, xwhiteout checks, and xino remapping. It can call overlay lookup and `vfs_getattr()` to keep `d_ino` consistent with `st_ino` for origin-backed entries.

`ovl_remap_lower_ino()` maps lower inode numbers into fsid-specific high-bit ranges when xino is active. It warns on overflow if `xino=on`.

`ovl_iterate_real()` uses `struct ovl_readdir_translate` to adjust `..`, impure upper entries, and lower xino mappings during direct real iteration.

## File Operations

`ovl_dir_operations` provides:

- `open`: opens the current real dir backing the overlay dir.
- `iterate_shared`: wrapped `ovl_iterate()`.
- `llseek`: delegates to real dir if possible, otherwise seeks within the merged cache.
- `fsync`: syncs the upper real dir when one exists and sync is not skipped.
- `release`: drops cache, real files, and per-open state.
- `read`: `generic_read_dir`.
- `setlease`: `generic_setlease`.

`ovl_dir_real_file()` returns the real dir file and lazily opens/caches the upper file if a lower dir was copied up after open.

## Cleanup Helpers

`ovl_check_empty_dir()` builds a merged view to determine whether a directory is empty, preserving upper whiteouts for later cleanup.

`ovl_cleanup_whiteouts()` removes selected upper whiteouts.

`ovl_workdir_cleanup()` and `ovl_workdir_cleanup_recurse()` clean stale workdir entries, with special handling for `work/incompat` feature markers.

`ovl_indexdir_cleanup()` scans indexdir entries, verifies each index entry, removes stale entries, and whiteouts orphan entries when NFS export requires stale handle blocking.

## Dependencies And Integration

This file depends on lookup/path helpers from `namei.c`, state helpers from `util.c`, cleanup/create helpers from `dir.c`, and mount feature state from `super.c`/`params.c`.

## Risk Notes

- Directory offsets are cache-position based for merged dirs, so cache invalidation through inode versioning is essential.
- Whiteout and xwhiteout filtering must be correct to avoid exposing hidden lower files.
- xino overflow handling affects user-visible inode identity.
- Work/index cleanup runs during mount setup and can determine whether a mount is allowed to proceed.
