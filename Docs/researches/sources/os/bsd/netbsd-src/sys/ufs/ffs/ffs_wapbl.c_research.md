# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_wapbl.c

This file integrates FFS with NetBSD WAPBL write-ahead physical block logging. It finds or creates journal storage, starts/stops logging, replays logs, cleans replayed inodes, and supplies WAPBL callbacks for metadata deallocation.

Key responsibilities:
- Determine whether the superblock layout supports WAPBL.
- Locate existing journals from superblock fields.
- Allocate a new journal either after the filesystem in the partition or inside the filesystem.
- Start, stop, and replay WAPBL logs.
- Record journal location in the superblock.
- Remove/clear old journal metadata.
- Complete logical cleanup after replay.
- Free or reallocate blocks during WAPBL sync/abort callbacks.

Important functions:
- `ffs_superblock_layout`: Distinguishes old UFS1 layout from UFS2-style superblock layout; WAPBL requires layout 2.
- `ffs_wapbl_replay_finish`: Processes replay cleanup records for unlinked inodes, vgets them, and frees mode-zero partially allocated inodes.
- `ffs_wapbl_sync_metadata`: WAPBL callback that applies delayed block frees, clears `fs_fmod`, updates `fs_time`, and writes summaries.
- `ffs_wapbl_abort_sync_metadata`: Reallocates blocks from aborted deallocation records.
- `wapbl_remove_log`: Clears journal locator fields and, for in-filesystem logs, zeroes the hidden log inode link count.
- `ffs_wapbl_start`: Enables logging when `MNT_LOG` is set, optionally clears old logs, finds/creates journal storage, flushes delayed buffers on update mounts, calls `wapbl_start`, sets `FS_DOWAPBL`, flushes the log, disables discard if needed, and completes replay cleanup.
- `ffs_wapbl_stop`: Flushes WAPBL, clears `FS_DOWAPBL` in a final transaction, stops the log, and handles forced stop.
- `ffs_wapbl_replay_start`: Locates the journal and initializes replay state with `wapbl_replay_start`.
- `wapbl_log_position`: Uses existing superblock journal locators if valid; otherwise chooses end-of-partition storage if sufficiently large, or creates an in-filesystem log, then writes journal locator metadata.
- `wapbl_create_infs_log`: Creates a hidden regular inode with `SF_LOG`, gives it one link, updates it, and allocates contiguous log storage.
- `wapbl_allocate_log_file`: Chooses a contiguous free extent, stores first data/indirect hints in the inode, allocates the file with `GOP_ALLOC`, and returns physical log start/count plus inode number.
- `wapbl_find_log_start`: Searches cylinder groups from the middle outward for a contiguous free extent large enough for the log plus needed indirect blocks.

Important interactions:
- Called by `ffs_mount`, `ffs_mountfs`, `ffs_unmount`, and `ffs_flushfiles`.
- Journal metadata is stored in `fs_journal_version`, `fs_journal_location`, `fs_journal_flags`, and `fs_journallocs[]`.
- Uses block bitmap helpers from `ffs_subr.c`, allocation via genfs/UFS paths, and WAPBL core APIs.
- Disables `MNT_DISCARD` when logging starts because discard conflicts with deallocation registration.

Notable behavior and risks:
- End-of-partition journal is preferred when the partition has enough space after the filesystem.
- In-filesystem journals require a contiguous free run and may fail with `ENOSPC` even when total free space is larger.
- Forced stop can leave `FS_DOWAPBL` state recovery to later handling.
- Several comments note duplicated journal-location logic across kernel and userland tools.
