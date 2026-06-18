# File Research: sources/local-fs/btrfs-progs/cmds/restore.c

## Purpose

Implements `btrfs restore`, an offline best-effort file recovery command for damaged unmounted filesystems. It opens trees in partial/read-only style, walks directory and extent metadata manually, and copies files, directories, symlinks, metadata, xattrs, snapshots, or matching paths into an output directory.

## Main Features

- Supports zlib, optional LZO, and optional ZSTD decompression.
- Can restore metadata, symlinks, snapshots, and xattrs.
- Can list roots, choose backup super, tree bytenr, fs root bytenr, or root objectid.
- Supports dry-run, overwrite, ignore-errors, regex path filtering, and first-directory discovery.

## Control Flow

1. `cmd_restore()` parses options, refuses mounted filesystems, and opens the filesystem through `open_fs()`.
2. `open_fs()` tries backup superblocks and uses partial/no-block-group/transid-mismatch flags to tolerate damage.
3. For restore mode, `search_dir()` recursively scans `BTRFS_DIR_INDEX_KEY` items from a root directory.
4. Regular files are opened and copied through `copy_file()`.
5. `copy_file()` walks `BTRFS_EXTENT_DATA_KEY` items and dispatches inline extents to `copy_one_inline()` and regular extents to `copy_one_extent()`.
6. Direct extents are read from mirrors via `read_data_from_disk()`, retrying mirrors on read/decompression failure.
7. Directory metadata and xattrs are applied after child traversal.
8. Symlinks are restored through `copy_symlink()` when requested.

## State

Global buffers and flags carry current path/output state and selected restore behavior:

- `fs_name`, `path_name`, `symlink_target`
- `get_snaps`, `restore_metadata`, `restore_symlinks`, `ignore_errors`, `overwrite`, `get_xattrs`, `dry_run`

## Dependencies

Uses btrfs-progs disk/tree/extent/file item APIs, compression libraries, path utilities, xattr/syscall APIs, regex, and shared open/mount checks.

## Risks And Edge Cases

- It intentionally tolerates damaged metadata and manually walks leaves, so output may be partial and errors may be skipped with `-i`.
- `copy_one_inline()` reads inline data into a fixed 4096-byte stack buffer; correctness depends on inline item size staying within that buffer.
- `copy_one_extent()` allocates buffers based on on-disk extent sizes, which can be large or corrupt.
- `overwrite_ok()` takes a `path` parameter but calls `fstatat()` on global `path_name`; current callers pass the same value, but the API is misleading.
- Recursive path construction uses fixed `PATH_MAX` buffers and rejects overflow through `path_cat_out()`/length checks.
