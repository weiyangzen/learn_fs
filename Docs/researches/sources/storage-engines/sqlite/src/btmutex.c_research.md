# sources/storage-engines/sqlite/src/btmutex.c

## Purpose

`btmutex.c` implements mutex entry and leave helpers for `Btree` and `BtShared` objects when shared cache is available. Its job is to make non-recursive `BtShared` mutexes appear recursively enterable at the `Btree` API boundary, while enforcing a global lock order across all btrees on a connection to avoid deadlocks.

## Important APIs, Types, And Functions

The main entry points are `sqlite3BtreeEnter()`, `sqlite3BtreeLeave()`, `sqlite3BtreeEnterAll()`, `sqlite3BtreeLeaveAll()`, `sqlite3BtreeEnterCursor()`, and, for threadsafe incremental blob builds, `sqlite3BtreeLeaveCursor()`. Debug-only assertions use `sqlite3BtreeHoldsMutex()`, `sqlite3BtreeHoldsAllMutexes()`, and `sqlite3SchemaMutexHeld()`.

Internal helpers are `lockBtreeMutex()`, `unlockBtreeMutex()`, `btreeLockCarefully()`, `btreeEnterAll()`, and `btreeLeaveAll()`. The key fields are `Btree.sharable`, `Btree.locked`, `Btree.wantToLock`, sorted `Btree.pNext/pPrev` links, `Btree.pBt`, `Btree.db`, `BtShared.mutex`, and `BtShared.db`.

## Control Flow

`sqlite3BtreeEnter()` first asserts that the connection mutex is already held and that the per-connection sharable btree list is sorted by `BtShared` address. Non-sharable btrees are no-ops. Sharable btrees increment `wantToLock`; if already locked, recursive entry returns immediately. Otherwise `btreeLockCarefully()` tries a nonblocking mutex acquire. On success it records the owning db and marks the btree locked.

If the try-lock fails, `btreeLockCarefully()` releases all currently held later locks in the same connection's sorted list, blocks on the requested lock, then reacquires later btrees that still have nonzero `wantToLock`. This preserves ascending `BtShared` lock order. `sqlite3BtreeLeave()` decrements `wantToLock` and releases the underlying mutex when the recursive count reaches zero.

`sqlite3BtreeEnterAll()` locks every sharable btree on the connection and sets `db->noSharedCache` when there were none, allowing future enter-all calls to skip the slow path. Leave-all mirrors this over all attached databases. In non-threadsafe shared-cache builds, only `BtShared.db` is assigned because mutex operations are compiled out.

## State And Persistence Behavior

The file manages synchronization state only; it does not persist database content. It mutates `Btree.wantToLock`, `Btree.locked`, `BtShared.db`, and `sqlite3.noSharedCache`. These fields protect schema and btree access elsewhere. Correctness depends on the connection mutex being held before these helpers run, because the shared-cache btree list and recursive counters are connection-local coordination structures.

## Dependencies And Integration Points

This code is compiled only when `SQLITE_OMIT_SHARED_CACHE` is not defined, with major branches for `SQLITE_THREADSAFE`. It depends on btree internal structures, SQLite mutex primitives, connection `aDb` entries, schema-to-index mapping, and incremental blob cursor ownership. Parser and schema code use enter-all before reading schemas across attached databases; pager/btree operations use enter/leave around individual shared btrees.

## Risks And Edge Cases

The central risk is deadlock or unlock imbalance. The sorted `pNext/pPrev` invariant, `wantToLock` reference count, and release/reacquire logic must remain consistent for all attached sharable btrees. Forgetting to hold the database mutex invalidates assumptions. `sqlite3SchemaMutexHeld()` treats TEMP schema specially because TEMP is connection-local. Non-threadsafe shared-cache builds still need `BtShared.db` updates even without mutexes, so replacing these functions with no-ops would break code that expects the owning db pointer.

## Test Signals

Signals include debug assertion coverage under shared-cache and threadsafe builds, concurrent connections sharing multiple btrees, enter-all/leave-all around schema parsing, recursive enter/leave nesting, incremental blob cursor entry, schema mutex assertions for main, temp, and attached schemas, and stress tests where two connections lock overlapping btree sets in different call orders without deadlock.
