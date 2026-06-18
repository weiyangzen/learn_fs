# File Research: sources/os/linux/linux/fs/gfs2/recovery.h

Declares the journal recovery interface and exposes the global recovery workqueue.

Key contents:
- Declares `gfs2_recovery_wq`.
- Defines `gfs2_replay_incr_blk()`, wrapping a journal block pointer at `jd_blocks`.
- Declares replay block read, revoke add/check/clean, journal recovery queueing, recovery work function, log-header validation, and log-pointer initialization APIs.

This header is consumed by mount, DLM recovery, log-operation replay, and journal code. Its central invariant is that all journal block iteration must wrap using the journal descriptor's block count.
