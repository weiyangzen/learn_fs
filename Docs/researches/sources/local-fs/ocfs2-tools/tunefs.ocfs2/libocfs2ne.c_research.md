# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/libocfs2ne.c

## Purpose
Shared implementation library for `tunefs.ocfs2` operations and debug feature executables. It handles filesystem opening, locking, signal safety, journal checks, allocator validation, online operation detection, feature/operation dispatch, and directory trailer migration support.

## Main Components
- `tunefs_filesystem_state` tracks the master filesystem, local exclusive fd, online mount fd, cluster lock status, allocator use, resized cluster count, max journal size, and journal feature bits.
- `tunefs_private` attaches per-open flags and shared state to each `ocfs2_filesys`.
- Global `fs_list` tracks all open filesystems for signal cleanup.
- Signal blocking uses a nesting counter around sensitive metadata writes.

## Operation Helpers
- `tunefs_get_number()` parses numeric strings with `K/M/G/T/P/B` suffixes.
- `tunefs_set_in_progress()` and `tunefs_clear_in_progress()` update resize/tunefs in-progress superblock bits.
- `tunefs_set_journal_size()` resizes every journal and optionally changes journal feature bits.
- `tunefs_empty_clusters()` writes zero blocks over a cluster range, falling back to smaller buffers on memory pressure.
- `tunefs_get_free_clusters()` reads global bitmap accounting.
- `tunefs_foreach_inode()` scans valid inodes and calls a supplied callback.

## Directory Trailer Support
- `tunefs_prepare_dir_trailer()` scans directory blocks, computes dirents that must move to make trailer space, and records affected blocks.
- `tunefs_install_dir_trailer()` optionally expands the directory, initializes new blocks with trailers, moves live dirents, writes new blocks first, then inode size, then modified old dirblocks.
- The write order is designed so interruption can leave duplicates but not lost entries, allowing fsck cleanup.

## Opening And Locking
- `tunefs_open()` wraps `ocfs2_open()` with tunefs safety checks:
  - Rejects heartbeat devices, resize-in-progress, and tunefs-in-progress for rw opens.
  - Uses `O_EXCL` for local filesystems.
  - Uses O2CB/O2DLM cluster locking for clustered filesystems.
  - Converts mounted rw volumes to online mode if the operation supports it.
  - Checks dirty journals for offline operations.
  - Opens the mount point for online ioctl operations.
  - Initializes a shared I/O cache when safe.
- `tunefs_close()` closes online descriptors, validates allocators after allocation operations, unlocks local/cluster state, removes private state, and closes the filesystem.

## Integrity Checks
- Allocation operations trigger global bitmap/chain validation on open and again on master close.
- Journal checks collect largest journal size and journal feature bits and reject dirty journals for offline operations.

## Dispatch
- `tunefs_feature_run()` opens a fresh filesystem for a feature, maps special open outcomes into operation flags, runs enable/disable, and closes.
- `tunefs_op_run()` does the same for generic operations.
- `tunefs_feature_main()` and `tunefs_op_main()` support standalone debug executables with common option parsing.

## Dependencies
- OCFS2 filesystem, inode, journal, allocator, DLM, mount, and I/O cache APIs.
- O2CB/O2DLM error tables and cluster stack support.
- `tools-internal` verbose/progress/interactive behavior.
- `libocfs2ne.h` public API and `o2ne_err.h` errors.

## Notes
This file is the safety core for the tunefs feature files. Feature implementations depend on it for clean-journal enforcement, locking, allocator validation, signal cleanup, and online/offline operation routing.
