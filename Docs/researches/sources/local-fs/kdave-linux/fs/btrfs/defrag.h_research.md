# File Research: sources/local-fs/kdave-linux/fs/btrfs/defrag.h

Small Btrfs defragmentation interface header for file defrag, autodefrag lifecycle, queued inode processing, root defrag, and cancellation checks.

Key responsibilities:
- Declares `btrfs_defrag_file()` for ioctl/autodefrag file extent rewriting over a range with generation and sector-count limits.
- Declares autodefrag slab-cache init/exit functions.
- Declares queue, run, and cleanup helpers for autodefrag inode records.
- Declares `btrfs_defrag_root()` for metadata tree defragmentation.
- Provides `btrfs_defrag_cancelled()`, currently implemented as a signal-pending check on the current task.

Dependencies:
- Includes Linux integer and compiler-type definitions.
- Forward-declares Btrfs inode, filesystem info, root, transaction, ioctl range args, and `file_ra_state`.

Notable risks:
- Cancellation is signal-based only; callers needing filesystem-wide cancellation must combine it with closing/remount checks.
- The header exposes both file and metadata defrag entry points, which have different locking and transaction expectations.
