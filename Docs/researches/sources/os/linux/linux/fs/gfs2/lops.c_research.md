# File Research: sources/os/linux/linux/fs/gfs2/lops.c

Implements low-level journal operations for metadata buffers, journaled data buffers, and revoke records. It also provides shared journal I/O helpers, journal-head search, pin/unpin transitions, and replay handlers.

Key exported functions include `gfs2_pin`, `gfs2_log_incr_head`, `gfs2_log_bmap`, `gfs2_log_submit_write`, `gfs2_log_write`, `gfs2_find_jhead`, and `gfs2_drain_revokes`.

Important behavior:
- `gfs2_pin()` clears dirty state, marks buffers pinned, moves already-written AIL entries, and increments pinned-log accounting.
- `gfs2_unpin()` marks buffers dirty again after log write, attaches them to transaction AIL1, updates glock AIL membership, and handles rgrp clone/discard bookkeeping.
- Journal writes are batched in bios via `gfs2_log_get_bio()` and completed by `gfs2_end_log_write()`, which unlocks page-cache buffers or frees mempool pages.
- `gfs2_find_jhead()` scans mapped journal extents using large bio batches to locate the highest valid log header sequence.
- `gfs2_before_commit()` writes descriptor blocks followed by payload blocks, sorting buffers by disk block number and escaping journaled data whose first word matches `GFS2_MAGIC`.
- Metadata replay scans `GFS2_LOG_DESC_METADATA` records, checks revokes, copies log blocks back to in-place metadata buffers, validates metadata, and syncs the journal inode glock.
- Revoke commit writes revoke descriptor and continuation blocks; revoke replay builds an in-memory revoke list on pass 0 and clears it after pass 1.
- Journaled data replay handles `GFS2_LOG_DESC_JDATA`, including unescaping.
- `gfs2_log_ops[]` registers operation order: databuf, buf, revoke.

This file ties the abstract log flush/recovery code to concrete on-disk log descriptor formats. Risk areas include descriptor length/count accounting, buffer pin lifetime, escaped-buffer copy correctness, bio completion, and replay ordering across revoke and payload passes.
