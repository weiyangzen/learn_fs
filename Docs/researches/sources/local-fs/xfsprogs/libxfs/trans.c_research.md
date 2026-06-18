# File Research: sources/local-fs/xfsprogs/libxfs/trans.c

## Role

`trans.c` implements the userspace libxfs transaction facade. It preserves the kernel transaction/log item model enough for shared metadata code to run in xfsprogs, but commits by applying superblock deltas and writing dirty buffers/inodes directly through libxfs rather than writing an active journal.

## Major Responsibilities

- Initialize transaction reservation tables with `libxfs_trans_init`.
- Allocate, reserve, roll, commit, cancel, and free transactions.
- Attach and detach buffer and inode log items to transactions.
- Implement transaction-aware buffer get/read/superblock lookup paths.
- Track buffer recursion counts and hold flags while buffers are joined to a transaction.
- Mark buffers dirty, log byte ranges, invalidate buffers, and tag inode-allocation buffers.
- Track superblock counter deltas and reservation usage.
- Run item precommit callbacks in a stable sorted order.
- Finish deferred operations on final permanent-transaction commit.
- Flush inode log items through `libxfs_iflush_int` and mark buffer log items dirty.
- Provide convenience transaction allocation for inode and directory updates.
- Allow clean transactions to reserve more blocks after metadata analysis.

## Transaction Lifecycle

`libxfs_trans_alloc` allocates a zeroed transaction, initializes item/defer lists, and reserves blocks, realtime extents, and log reservation metadata. Userspace reservation checks compare requested data blocks against `sb_fdblocks` and realtime extents against `sb_rextents`, but do not perform quota reservations.

`libxfs_trans_roll` duplicates the transaction's permanent reservation state, commits the current transaction with `regrant=true`, and reserves the log space for the next transaction. The duplicate inherits unused block reservation and deferred ops; the original is prevented from allocating further by reducing its block reservation to what it already used.

`libxfs_trans_cancel` aborts if the transaction is dirty, because userspace has no journal recovery path for a dirty cancellation. Deferred ops on cancel are treated as dirty and cancelled only after assertions/diagnostics.

## Buffer Item Handling

`libxfs_trans_get_buf_map` and `libxfs_trans_read_buf_map` first search for a matching buffer already joined to the transaction. A hit increments `bli_recur`; a miss obtains or reads a normal libxfs buffer and joins it with `_libxfs_trans_bjoin`.

`libxfs_trans_brelse` only releases clean, non-stale, non-dirty buffers whose recursion count is zero. Dirty or invalidated buffers stay attached until commit. `libxfs_trans_bdetach` forcibly removes a completely clean, unheld buffer from a transaction while leaving the caller's locked reference intact.

`libxfs_trans_log_buf` marks the transaction and buffer item dirty and records the logged byte range. `libxfs_trans_binval` stales a buffer, cancels delayed write, clears dirty state, marks the log item cancel/stale, and dirties the transaction.

## Commit Path

`__xfs_trans_commit` runs precommit callbacks, finishes deferred ops on the final commit of permanent transactions, reruns precommits for the final deferred-op transaction, applies superblock deltas, calls `xfs_log_sb`, and then completes every log item. Buffer items are marked dirty and released unless held. Inode items flush inode core/fork state through `libxfs_iflush_int`, dirty the backing inode buffer on success, and release it.

On precommit or defer errors, the transaction items are detached/unlocked and the transaction is freed. Dirty commit failures force shutdown via the same shared XFS mechanisms used by kernel-derived code.

## Superblock Accounting

`libxfs_trans_mod_sb` tracks only fields needed in userspace: free data blocks, inode count, free inode count, and free realtime extents. Negative free-block and realtime deltas consume transaction reservations and assert if usage exceeds reservation. `XFS_TRANS_SB_RES_FDBLOCKS` is ignored because it only affects on-disk reservation accounting in this userspace model.

## Notable Assumptions

- Userspace does not need real log space but still maintains permanent-log-reservation flags to satisfy shared-code assertions.
- Dirty transaction cancellation is fatal.
- Ordered buffers are treated like ordinary logged dirty buffers because userspace commits directly.
- Precommit item sorting uses optional `iop_sort` callbacks; unsortable items are moved later.
- `libxfs_trans_alloc_dir` always sets `nospace_error` to zero because userspace does not support kernel reservationless creation fallback.
