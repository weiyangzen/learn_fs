# sources/user-network-fs/samba/source3/include/g_lock.h

## Purpose
`g_lock.h` declares a global lock abstraction built on dbwrap and Samba messaging. It supports read/write/upgrade/downgrade locks, async locking, lock callbacks, data associated with locks, dumps, sequence numbers, and watcher wakeups.

## Important APIs, Types, And Functions
- Opaque `g_lock_ctx` and `g_lock_lock_cb_state` represent lock manager and active callback state.
- `enum g_lock_type` defines read, write, upgrade, and downgrade requests.
- Context creation: `g_lock_ctx_init_backend()` and `g_lock_ctx_init()`, plus `g_lock_set_lock_order()`.
- Lock operations: async `g_lock_lock_send/recv()`, sync `g_lock_lock()`, and `g_lock_unlock()`.
- Callback helpers dump, write data, unlock, watch blocker death, and wake watchers from inside callback state.
- Data helpers: `g_lock_writev_data()`, `g_lock_write_data()`.
- Introspection: `g_lock_locks_read()`, `g_lock_locks()`, `g_lock_dump_send/recv()`, `g_lock_dump()`, `g_lock_seqnum()`.
- Watch APIs: `g_lock_watch_data_send/recv()` and `g_lock_wake_watchers()`.

## Control Flow
Callers initialize a context with messaging and backend dbwrap state, request a lock on a `TDB_DATA` key, receive a callback when the lock can be acted on, optionally write lock-associated data, and unlock. Async variants integrate with tevent; sync wrappers wait with a timeout.

## State And Persistence
Lock state and optional data are stored in the dbwrap backend and coordinated via messaging. Watchers observe blocker death or explicit wakeups. Sequence numbers expose state changes.

## Dependencies And Integration Points
It depends on server IDs, dbwrap, messaging, TDB data buffers, tevent, and CTDB/Samba messaging infrastructure. It is used by clustered or multi-process subsystems needing cross-process synchronization.

## Risks
Lock ordering is critical to avoid deadlocks. Callback code must unlock correctly and avoid blocking. Watcher semantics depend on accurate process liveness. Data writes under locks must fit backend atomicity guarantees.

## Test Signals
Test read/write compatibility, upgrades/downgrades, timeout behavior, dead owner detection, watcher wakeups, lock dump data, sequence increments, backend lock order, and multi-process contention.
