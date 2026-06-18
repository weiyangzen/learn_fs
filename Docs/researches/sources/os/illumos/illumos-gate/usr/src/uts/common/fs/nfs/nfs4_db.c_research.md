# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_db.c

Purpose: Implements the generic NFSv4 server state database used by server-side state tables.

Key behavior:
- Creates/destroys NFSv4 state databases, tables, indexes, hash buckets, ID spaces, and per-table kmem caches.
- Manages database entry lifecycle: allocation, constructor/destructor callbacks, refcounts, invalidation, hide/unhide, locking, timed waits, and condition broadcasts.
- `rfs4_dbsearch` searches a hash index, optionally creates a new entry through a single createable index, assigns IDs, and links the entry into all table indexes.
- Provides table walking and search-with-callback helpers that lock entries while invoking callers.
- Starts one reaper thread per expiring table; reapers reclaim entries with only the table hash reference left and either expired by policy or during shutdown.
- Handles database shutdown by marking all table reapers for exit and waiting for each to report completion.

Dependencies:
- Uses illumos kernel synchronization, kmem caches, ID space allocator, zthreads, callb CPR support, DTrace probes, and NFSv4 server structures from `nfs4_db_impl.h`.

Notable details:
- Table reap interval dynamically tightens as ID usage crosses low/high watermarks.
- Entries are linked into multiple indexes but only receive one table/hash reference.
- Index link invalidation uses a low-bit pointer marker to catch misuse.
- Resume-from-suspend callback extends client last-access times by one lease period.
