# File Research: sources/os/linux/linux/fs/gfs2/log.c

Implements GFS2 journal space accounting, log reservation, AIL management, ordered write handling, revoke handling, log flush orchestration, and the `gfs2_logd` kernel thread.

Key exported functions include `gfs2_struct2blk`, `gfs2_log_is_empty`, `gfs2_log_release_revokes`, `gfs2_log_release`, `gfs2_log_try_reserve`, `gfs2_log_reserve`, `gfs2_write_log_header`, `gfs2_remove_from_journal`, `gfs2_log_flush`, `gfs2_log_commit`, `gfs2_ail1_flush`, `log_flush_wait`, `gfs2_add_revoke`, `gfs2_glock_remove_revoke`, `gfs2_flush_revokes`, `gfs2_ail_drain`, and `gfs2_logd`.

Important behavior:
- AIL1 tracks buffers that still need in-place writeback; AIL2 tracks transactions whose buffers have been written and whose log space can be released after tail movement.
- `gfs2_ail1_flush()` starts writeback via inode mappings, handles jdata holes, detects long stuck flushes, and withdraws on serious writeback errors.
- Reservation paths account for both journal blocks and revokes; non-logd callers preserve `GFS2_LOG_FLUSH_MIN_BLOCKS` so logd can still flush.
- `calc_reserved()` computes live reservation needs for metadata, journaled data, descriptor blocks, revokes, and headers.
- Ordered-data mode writes and waits on ordered inode mappings before committing the log header.
- `gfs2_write_log_header()` builds on-disk log headers with hashes, CRCs, sequence/tail/head metadata, local statfs/quota inode references, and block mapping.
- `__gfs2_log_flush()` serializes flushes, detaches the incore transaction, runs log-operation commit hooks, writes headers, drains AIL for sync/shutdown/freeze flushes, and handles withdraw cleanup.
- `log_refund()` merges completed transactions into `sd_log_tr`, recomputes actual reservation needs, and releases unused blocks.
- `gfs2_logd()` wakes on pinned/log pressure or periodic timeout, flushes journal blocks, and starts AIL writeback as thresholds are crossed.

The file is central to GFS2 crash consistency. Risk areas include reservation/refund balance, revoke accounting, withdraw paths during partial flush, AIL list locking, and ensuring ordered data reaches disk before the committing log header.
