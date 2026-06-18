# File Research: sources/os/linux/linux/fs/overlayfs/file.c

## Role

Implements OverlayFS regular file operations by forwarding I/O to the current real backing file while preserving overlay copy-up semantics.

## Main Responsibilities

- Opens real backing files with overlay credentials after checking real inode permissions.
- Stores per-open state in `struct ovl_file`, including the initially opened real file and an optional lazily opened upper file.
- `ovl_real_file_path()` switches from lower to upper file after copy-up or for metacopy fsync paths and synchronizes changed open flags.
- `ovl_open()` verifies lower data, performs copy-up if open flags require it, strips creation/truncate-only flags, opens the real data path, and stores private data.
- Forwards `llseek`, `read_iter`, `write_iter`, `splice_read`, `splice_write`, `fsync`, `mmap`, `fallocate`, `fadvise`, `copy_file_range`, `remap_file_range`, `flush`, and lease setup.
- Updates overlay inode attributes after writes, fallocate, copy, clone, and dedupe operations.
- Handles O_DIRECT flag validation and O_APPEND immutability restrictions in `ovl_change_flags()`.

## Important Control Flow

Reads resolve the current real data file and call `backing_file_read_iter()` with overlay credentials and an access callback. Writes lock the overlay inode, refresh attributes, resolve the real file, optionally mask sync flags depending on overlay sync policy, and call `backing_file_write_iter()`.

`ovl_fsync()` avoids syncing lower files to prevent read-only filesystem errors. It only syncs upper paths when the overlay sync policy requires it and the object has upper data.

`ovl_remap_file_range()` permits clone/copy through real files, but refuses dedupe unless both input and output are already upper, because dedupe-triggered copy-up would defeat deduplication semantics.

## Dependencies

Uses `backing_file_*` helpers, overlay credentials, copy-up path selection, realdata verification, and VFS file-range APIs.

## Research Notes

This file is the open-file indirection layer. Its key invariant is that an overlay file descriptor continues to work correctly even if the dentry’s data source changes from lower/metacopy to upper after copy-up.
