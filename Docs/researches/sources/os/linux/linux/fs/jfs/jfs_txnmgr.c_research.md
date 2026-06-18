# File Research: sources/os/linux/linux/fs/jfs/jfs_txnmgr.c

Implements JFS transaction management: transaction/tlock allocation, metadata locking, log record generation, commit sequencing, persistent/working map updates, lazy commit, quiesce, and tlock-starvation relief.

Global state:
- `TxAnchor` tracks free transaction IDs, free lock words, wait queues, tlock pressure, lazy-commit queues, and anonymous transaction inode lists.
- `TxBlock` is the transaction block table; `TxLock` is the transaction lock table.
- Tunables `nTxBlock` and `nTxLock` size the tables, bounded to 65536 entries.
- Low/high/very-high tlock watermarks wake `jfsSyncThread` and throttle new transactions.

Initialization:
- `txInit()` sizes and allocates transaction and lock tables, initializes wait queues/lists, and builds freelists.
- `txExit()` frees the tables.

Transaction lifecycle:
- `txBegin()` waits for log barriers/quiesce/tlock pressure/free tblocks, allocates a tblock, assigns a log transaction id, and increments log activity.
- `txBeginAnon()` gates anonymous metadata updates on barriers and tlock pressure without allocating a tblock.
- `txEnd()` wakes waiters, returns a tblock to the freelist, and if the last active transaction drains a sync barrier, writes a hard syncpoint and wakes blocked starters.
- `txAbort()` frees tlocks, clears metapage bindings/logsync state, and can mark the filesystem dirty.

Locking:
- `txLock()` binds a tlock to a metapage or in-memory inode, handles directory xtree special cases, transfers anonymous tlocks into a real transaction, initializes linelock/xtlock state, and waits only for expected aggregate-map conflicts.
- `txMaplock()` creates map-update-only tlocks for extent allocation/free work.
- `txLinelock()` chains additional line-vector lock storage.
- `txFreelock()` frees anonymous tlocks marked `tlckFREELOCK`.

Commit path:
- `txCommit()` sorts inodes by descending inode number, transfers anonymous tlocks, writes on-disk inode tlocks via `diWrite()`, dispatches all tlocks through `txLog()`, writes the COMMIT record, waits or queues group commit, optionally forces careful-update pages, updates maps, releases tlocks/metapages, and resets inode commit state.
- `txLog()` dispatches by tlock type to `xtLog`, `dtLog`, `diLog`, `mapLog`, or `dataLog`.
- `diLog()` logs inode after-images or freed inode extents.
- `dataLog()` logs directory table/data metapages and discards obsolete inline table pages.
- `dtLog()` logs directory tree page after-images, new/extended pages, noredo records, and block-map updates.
- `xtLog()` handles xtree growth, deletion, truncation, relocation-related map records, lazy-commit-safe extent snapshots, and force-synchronous cases when map data points into mutable xtree pages.
- `mapLog()` logs standalone allocation/free map updates, including relocation source extents.
- `txEA()` records extended attribute/ACL extent allocation/free maplocks or inline-EA commit flags.

Map and page completion:
- `txForce()` reverses tlock order for careful update and synchronously writes selected metapages.
- `txUpdateMap()` applies persistent and/or working map changes for block allocation/free and inode create/delete.
- `txAllocPMap()` marks allocated extents in the persistent block map and clears new/extended XAD flags.
- `txFreeMap()` frees extents from persistent and/or working maps.
- `txRelease()` unbinds tlocks from metapages before home writes are allowed.
- `txUnlock()` marks metapages homeok, propagates committed LSNs, removes tblocks from the log sync list, and frees tlocks.

Background paths:
- `txLazyUnlock()` queues committed lazy transactions.
- `jfs_lazycommit()` processes the lazy unlock queue while preserving per-superblock transaction order.
- `txLazyCommit()` updates maps, marks group commit complete, wakes waiters, unlocks tlocks, and ends lazy transactions.
- `txQuiesce()` blocks new transactions and commits anonymous inodes.
- `txResume()` clears quiesce and wakes waiters.
- `jfs_sync()` runs when tlocks are low, committing inodes on the anonymous transaction list.

Important invariants:
- Tlock list order matters for truncate and map update correctness.
- Lazy commit is disabled when maplocks point into mutable xtree pages that might change before `txUpdateMap()`.
- Log durability precedes home writes and persistent map updates.
- Allocation map pages inherit transaction LSNs so syncpoints cannot advance past required recovery information prematurely.
