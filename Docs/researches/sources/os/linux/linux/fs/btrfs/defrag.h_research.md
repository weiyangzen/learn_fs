# File Research: sources/os/linux/linux/fs/btrfs/defrag.h

## Purpose

Declares the Btrfs defragmentation interface used by ioctl paths, autodefrag scheduling, filesystem lifecycle, and metadata root defrag.

## Main Responsibilities

- Forward declare types needed by defrag callers.
- Declare file defrag, autodefrag init/exit, queue management, autodefrag execution, cleanup, and root defrag APIs.
- Provide the cancellation helper.

## Declared Interfaces

- `btrfs_defrag_file()`:
  - Defrags a file range described by `btrfs_ioctl_defrag_range_args`.
  - Accepts readahead state, transaction-generation threshold, and max sectors to defrag.

- `btrfs_auto_defrag_init()` / `btrfs_auto_defrag_exit()`:
  - Create and destroy autodefrag slab state.

- `btrfs_add_inode_defrag()`:
  - Queue an inode for automatic defrag with an extent-size threshold.

- `btrfs_run_defrag_inodes()`:
  - Run queued autodefrag work for a filesystem.

- `btrfs_cleanup_defrag_inodes()`:
  - Free queued autodefrag records.

- `btrfs_defrag_root()`:
  - Defrag metadata tree blocks for a root.

- `btrfs_defrag_cancelled()`:
  - Inline cancellation predicate; currently returns `signal_pending(current)`.

## Dependencies And Notes

- Includes Linux type/compiler headers only.
- Uses forward declarations to avoid pulling large Btrfs headers into every includer.
- `btrfs_defrag_cancelled()` takes `fs_info` but currently does not inspect it, leaving room for future filesystem-level cancellation logic.
