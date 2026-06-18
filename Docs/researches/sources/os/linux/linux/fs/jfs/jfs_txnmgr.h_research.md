# File Research: sources/os/linux/linux/fs/jfs/jfs_txnmgr.h

Declares transaction manager structures, flags, lock overlays, and public APIs.

Primary structures:
- `struct tblock` is a transaction block. It shares the logsync prefix layout, stores superblock, tlock chain, wait queues, log transaction id, group-commit queue state, commit LSN/page/EOR, and create/delete payload.
- `struct tlock` is a transaction lock word bound to a metapage or inode, with overlay storage for line locks, xtree locks, or map locks.
- `struct linelock` describes modified byte-line ranges that `lmWriteRecord()` copies into the journal.
- `struct xtlock` extends linelock data with xtree watermarks and inline PXD storage.
- `struct maplock`, `struct xdlistlock`, and `pxd_lock` encode extent allocation/free work for later map updates.
- `struct commit` bundles commit-time context and an `lrd`.

Flags:
- Commit flags cover sync/force/lazy, map update type, create/delete/truncate, metapage, and inode commits.
- Tlock flags distinguish page/inode/line locks, logged state, map updates, directory locks, free locks, writepage, and freepage.
- Tlock type/operation bits distinguish inode, xtree, dtree, map, EA/ACL, data, btree root, grow, truncate, relocate, new/free/relink operations.
- Maplock flags distinguish allocation/free of XAD/PXD singletons or lists.

Exports:
- Initialization: `txInit`, `txExit`.
- Transaction lifecycle: `txBegin`, `txBeginAnon`, `txEnd`, `txCommit`, `txAbort`.
- Locking/map helpers: `txLock`, `txMaplock`, `txLinelock`, `txFreeMap`, `txEA`, `txFreelock`.
- Journal bridge: `lmLog`.
- Background/quiesce: `txQuiesce`, `txResume`, `txLazyUnlock`, `jfs_lazycommit`, `jfs_sync`.

Integration:
- Includes `jfs_logmgr.h`, so transaction code can share log record types and group-commit state.
