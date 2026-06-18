# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_txnmgr.c

## Role

Implements the JFS transaction manager: transaction/tlock allocation, transaction begin/end, metadata locking, commit logging, map updates, abort, lazy commit, quiesce/resume, and background sync for anonymous transactions.

## Main Responsibilities

- `txInit()` sizes and allocates global `TxBlock` and `TxLock` tables, sets tlock low/high watermarks, initializes wait queues and anonymous/lazy lists.
- `txBegin()` starts a transaction, respecting log sync barriers, quiesce state, tlock pressure, and free tblock availability.
- `txBeginAnon()` gates anonymous updates on the same barrier and tlock pressure rules.
- `txEnd()` returns the tblock to the free list, handles lazy-commit unlock handoff, decrements active transaction count, and clears log sync barriers after a hard sync point.
- `txLock()` binds a transaction lock to a metapage or inode, handles directory xtree special locking, transfers anonymous tlocks to real transactions, marks metapages `nohomeok`, and initializes line/xtree lock overlays.
- `txMaplock()` creates map-only tlocks for extent allocation/free records.
- `txLinelock()` allocates extra line-vector capacity when a tlock needs more line descriptors.
- `txCommit()` sorts inodes by descending inode number, absorbs anonymous tlocks, writes disk inode state through `diWrite()`, logs all tlocks, writes `LOG_COMMIT`, runs group commit, optionally forces careful-update pages, updates maps, releases locks, and resets inode commit state.
- `txLog()` dispatches each tlock to `diLog`, `dataLog`, `dtLog`, `xtLog`, or `mapLog`.
- `txUpdateMap()` applies allocation/free effects to persistent and working maps, handles inode create/delete map updates, and discards freed metadata pages.
- `txAbort()` releases tlocks, resets metapage log sync state, and can mark the filesystem dirty.
- `jfs_lazycommit()` drains committed transactions from `TxAnchor.unlock_queue` while preserving per-superblock ordering.
- `jfs_sync()` commits inodes with anonymous tlocks when tlocks are scarce.
- `txQuiesce()` blocks new transactions and forces anonymous transactions to commit; `txResume()` clears quiesce.

## Logging Helpers

- `diLog()` logs inode page after-images or inode extent no-redo records and prepares map updates.
- `dataLog()` logs directory table data pages, with special handling for inline table truncation.
- `dtLog()` logs dtree after-images, no-redo records for freed pages, and maplock updates for page allocation/free.
- `xtLog()` handles xtree growth, free, truncate, relocation, root cases, and lazy-commit copy/force decisions for XAD/PXD lists.
- `mapLog()` logs block map update records for relocation, EA/ACL, and other data extent changes.
- `txEA()` prepares maplocks for external EA/ACL extent allocation/free and marks inline EA commits.

## Important State and Synchronization

- `jfsTxnLock` protects free tblock/tlock lists and anonymous transaction lists.
- `TxAnchor.LazyLock` protects the lazy unlock queue.
- `jfs_tlocks_low` triggers `jfsSyncThread`.
- Tlocks are overloaded with `linelock`, `xtlock`, `maplock`, and `xdlistlock` layouts.
- `COMMIT_LAZY` lets group commit return before map updates and lock release, with later completion by lazy commit thread.
- `COMMIT_FORCE` performs careful synchronous pageout and map update in caller context.

## Correctness Notes

- Metapages are marked `nohomeok` before logging to prevent home write before journal safety.
- Some lazy commits copy small extent lists into the tlock overlay; larger lists force synchronous commit because they point directly into mutable xtree pages.
- Inode locking order is explicitly sorted in `txCommit()` to reduce deadlock risk.
- Truncation and map-update paths are careful about persistent map versus working map differences.
