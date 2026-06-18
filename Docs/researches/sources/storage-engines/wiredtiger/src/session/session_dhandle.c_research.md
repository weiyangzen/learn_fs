# sources/storage-engines/wiredtiger/src/session/session_dhandle.c

## Purpose
Manages per-session data-handle lookup, caching, locking, checkpoint-handle resolution, release, sweep, and checkpoint locking. It is the session-side synchronization layer between URI-based operations and shared connection dhandle state.

## Important APIs, Types, and Functions
- `__wt_session_get_dhandle` locates, locks, opens, and installs `session->dhandle` for a URI/checkpoint.
- `__wt_session_get_btree_ckpt` interprets checkpoint configuration and opens matching data-store and optional history-store checkpoint handles with consistent snapshot metadata.
- `__wt_session_lock_dhandle` enforces read/write/exclusive locking, special-operation exclusion, and dead-handle handling.
- `__wt_session_release_dhandle_v2` closes bulk/special/discard handles as needed, unlocks read/write locks, decrements exclusive references, and clears `session->dhandle`.
- `__wt_session_close_cache` and `__wt_session_dhandle_sweep` discard cached dhandle references.
- `__wt_session_lock_checkpoint` locks checkpoint handles for overwrite and evicts cached checkpoint pages.
- `__wt_dhandle_clear_add` records debug breadcrumbs for dhandle clearing.

## Control Flow
Lookup first searches the session hash cache, discarding inactive/outdated non-metadata entries. On miss it sweeps stale session handles, searches the shared connection list under read lock, or allocates under write lock, then caches the acquired reference. Locking loops until the handle is open in a compatible mode, dead, busy, or exclusively acquired for open/special operations. If a handle must be opened but the caller lacks schema lock, it drops the temporary exclusive lock and recursively retries under schema lock, with special checkpoint-lock handling for disaggregated stable constituents.

Checkpoint opening has a retry loop for unnamed checkpoints. It reads snapshot wall times, datastore checkpoint metadata, optional history-store checkpoint metadata, and snapshot/timestamp metadata; detects races with running checkpoints; opens dhandles; validates checkpoint order; and retries `WT_NOTFOUND`/`EBUSY` for unnamed checkpoint races.

## State and Persistence Behavior
This file does not directly persist data, but it protects durable views by pinning the correct dhandles and checkpoint versions. It maintains session dhandle cache entries, shared dhandle reference counts, dhandle lock flags, exclusive owner/refcount, discard/dead/outdated flags, checkpoint snapshot metadata, history-store checkpoint pins, and checkpoint handle locks tracked by metadata tracking. Release paths can close handles, evict checkpoint pages, and mark discard-on-release to avoid stale checkpoint contents.

## Dependencies and Integration Points
Integrated with connection dhandle allocation/open/close/sweep, schema and checkpoint locks, metadata checkpoint readers, history-store URI selection, transaction snapshot metadata, eviction, metadata tracking, session reset/close, and all cursor/schema APIs that open btree handles.

## Risks
This is concurrency-critical code. Lock-order mistakes can deadlock schema, checkpoint, and handle-list locks. Race detection for checkpoint cursors depends on monotonic checkpoint wall times and order numbers. Incorrect reference counting or cache discard can produce use-after-free or leaked handles. Exclusive special-operation semantics must prevent bulk/salvage/verify/truncate conflicts without letting internal sweep starve user operations.

## Test Signals
Stress tests should cover concurrent cursor open/close/drop/verify/checkpoint, checkpoint cursor opens during active checkpoints, named and unnamed checkpoint regeneration, history-store checkpoint matching, disaggregated stable checkpoint handling, bulk-load close-on-release, dhandle sweep of dead/outdated handles, exclusive lock `EBUSY`, and metadata tracking rollback around checkpoint handle locks.
