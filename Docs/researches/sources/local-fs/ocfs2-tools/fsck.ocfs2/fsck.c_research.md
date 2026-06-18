# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/fsck.c

Read coverage: complete file read, 1163 lines.

Purpose: main `fsck.ocfs2` driver. It owns option parsing, device safety checks, cluster locking, journal replay, slot recovery, pass sequencing, superblock writeback, cleanup, and exit status.

Behavior:
- Supports `-n`, `-y`, `-p`/`-a`, `-f`, `-F`, `-b`, `-B`, `-r`, `-D`, `-G`, `-P`, `-t`, `-u`, `-v`, and `-V`.
- Refuses read-write checking on mounted/busy filesystems; warns and asks before read-only mounted checks or skipped cluster checks.
- Initializes error tables, progress display, signal handlers, and shared `o2fsck_state`.
- Can recover the primary superblock from a numbered backup superblock before opening normally.
- Opens the filesystem, validates minimal superblock state, locks the cluster via o2cb/DLM unless local/read-only/skipped, and prints filesystem identity.
- Checks journal files, decides whether journal replay is needed, replays dirty journals, closes/reopens after replay, then grows the I/O cache.
- Initializes inode/link/dir/cluster tracking state after journal replay.
- Runs slot recovery for local allocators, truncate logs, and orphan dirs, forcing a full check if recovery reports errors.
- Skips full pass work if the filesystem is clean and no force condition applies.
- Runs passes 0 through 5 in order, then writes superblock state, optionally clears dirty journal flags and jbd2 errno, and formats the slot map.
- Exit code is the fsck bitmask defined in `util.h`.

Key shared state:
- `o2fsck_state` tracks filesystem handle, allocator inodes, inode type bitmaps, allocated/duplicate clusters, inode/link reference counts, directory blocks, parent graph, refcount trees, prompt policy, repair flags, statistics, and progress/resource tracking.

Dependencies: all fsck pass modules, journal/slot recovery, libocfs2, libo2cb/libo2dlm cluster services, prompt framework, progress library.

Risk notes:
- `-F` is intentionally dangerous and guarded only by an interactive warning.
- `-n` opens read-only and skips journal replay/slot recovery, so later reported errors can be spurious.
- Memory allocation and most I/O/pass errors are treated as fatal.
- Signal handling attempts to release cluster resources and close the filesystem before exit.
