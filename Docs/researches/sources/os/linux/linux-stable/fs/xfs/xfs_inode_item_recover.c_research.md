# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_inode_item_recover.c

This file implements log-recovery handling for XFS inode log items. It registers `xlog_inode_item_ops`, providing readahead and pass-2 replay for `XFS_LI_INODE` records.

Key responsibilities:
- `xlog_recover_inode_ra_pass2` issues inode-buffer readahead from either native or 32-bit converted inode log formats.
- `xlog_recover_inode_commit_pass2` replays logged inode core and fork data into the inode buffer, with extensive validation before and after replay.
- `xfs_recover_inode_owner_change` handles post-replay btree owner rewrites needed after extent-swap recovery, instantiating a temporary `xfs_inode` directly from the recovered dinode to avoid `xfs_iget` and transaction-triggering inactive paths during log recovery.
- `xfs_log_dinode_to_disk` converts logged in-core dinode fields to ondisk big-endian fields, including bigtime timestamps, v3 inode fields, CRC LSN, UUID, and 64-bit extent counters.
- `xlog_dinode_verify_extent_counts` validates large extent count feature compatibility, padding, and `nextents + anextents <= nblocks`.
- `xlog_recover_inode_dbroot` converts logged data-fork btree roots into dinode-root format, including metadata btree roots for realtime rmap and realtime refcount files.

Important recovery flow:
1. Convert old log format if needed.
2. Skip replay if the target inode buffer was cancelled.
3. Read the inode buffer with inode-buffer verifiers.
4. Validate target inode magic and logged inode magic.
5. Compare ondisk inode LSN or legacy `di_flushiter` to avoid replaying stale records.
6. Validate file-type-specific fork formats, extent counts, fork offset, and log dinode size.
7. Replay core, device, data fork, and attr fork fields according to `ilf_fields`.
8. Apply owner-change replay for swapext metadata when required and inode is not deleted.
9. Recalculate CRC, verify the final dinode, mark the buffer as log-recovered, and queue it for delayed write.

Dependencies and integration:
- Uses log recovery interfaces from `xfs_log_recover.h`, buffer APIs, inode conversion helpers, bmap btree conversion, realtime metadata btree conversion, tracepoints, and corruption reporting.
- Interacts directly with delayed-write buffer recovery via `xfs_buf_delwri_queue`.
- The code is recovery-critical: it intentionally avoids normal inode cache lifecycle behavior where that could start transactions.

Risk notes:
- Correctness depends on carefully honoring log item field flags and iovec ordering.
- The owner-change replay path deliberately bypasses ordinary inode instantiation; verifier coverage after replay is therefore essential.
- LSN handling is subtle: logged dinode LSN is not trusted, so replay writes `current_lsn` into v3 dinodes.
