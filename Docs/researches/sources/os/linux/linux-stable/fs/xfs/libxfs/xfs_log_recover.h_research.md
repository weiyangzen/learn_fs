# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_log_recover.h

## Role
`xfs_log_recover.h` declares internal log recovery structures, item recovery operation hooks, recovered transaction state, buffer cancellation helpers, and intent recovery interfaces.

## Main Definitions
- `enum xlog_recover_reorder` classifies recovered items into buffer, generic item, inode buffer, or cancel lists for correct replay ordering.
- `struct xlog_recover_item_ops` is the per-log-item recovery vtable: item type, reorder hook, pass2 readahead, pass1 commit, and pass2 commit.
- `struct xlog_recover_item` stores recovered log item regions, operation hooks, and list linkage.
- `struct xlog_recover` tracks one recovered transaction, including transaction id, header, LSN, and recovered item queue.
- `XLOG_RHASH_*` defines the recovered transaction hash table layout.
- `XLOG_MAX_REGIONS_IN_ITEM` bounds region counts from the buffer dirty bitmap format.

## Exported Recovery Hooks
- Declares recovery ops for icreate, buffer, inode, dquot, quotaoff, bmap, extent free, rmap, refcount, attr, exchange-map, and realtime intent/done item types.
- Provides buffer readahead and cancellation table helpers.
- Provides inode lookup helpers for recovery by inode number and optional generation.
- Provides intent release, intent item reconstruction, and intent finish functions.

## Important Helper
- `xlog_recover_resv` converts a normal transaction reservation into a recovery reservation by keeping logres/logflags but forcing `tr_logcount = 1`, avoiding grant-space livelock while recovered intents pin the log tail.

## Dependencies
This header ties log recovery to deferred operation types, transaction reservations, in-core log items, buffer replay, inode cache lookup, and AIL intent item lifecycle.

## Research Notes
The key concept is two-pass recovery with per-item hooks. Intent items are reconstructed into in-core log items, paired done items release them, and unfinished intents are replayed through deferred operation recovery.
