# sources/storage-engines/sqlite/src/notify.c

Purpose: implements `sqlite3_unlock_notify()` and support routines for shared-cache lock wait notification when `SQLITE_ENABLE_UNLOCK_NOTIFY` is enabled.

Important APIs and state: exported/internal routines are `sqlite3_unlock_notify()`, `sqlite3ConnectionBlocked()`, `sqlite3ConnectionUnlocked()`, and `sqlite3ConnectionClosed()`. The central state is `sqlite3BlockedList`, a process-global linked list of connections whose `pBlockingConnection` or `pUnlockConnection` is non-null. Each connection stores callback pointer `xUnlockNotify`, callback argument, blocking connection, unlock connection, and list link.

Control flow: callers record a lock wait with `sqlite3ConnectionBlocked(db, blocker)`, which adds `db` to the blocked list if needed and sets `pBlockingConnection`. `sqlite3_unlock_notify()` holds both `db->mutex` and `SQLITE_MUTEX_STATIC_MAIN`; it cancels when callback is null, invokes immediately if no blocker remains, detects deadlock by walking the unlock chain back toward `db`, or records the desired blocker/callback and groups the connection by callback in the blocked list. `sqlite3ConnectionUnlocked(db)` scans the list when a transaction releases locks, clears references to `db`, batches callback arguments for identical callback functions, removes completed entries, and invokes callbacks. `sqlite3ConnectionClosed()` treats close as unlock, removes the connection, and verifies no remaining blocked entries reference it.

State and persistence: all state is in-process and protected by `STATIC_MAIN`. Debug `checkListProperties()` asserts that entries are meaningful, callback groups are contiguous, and close cleanup removed references.

Dependencies and integration points: depends on `sqliteInt.h`, `btreeInt.h`, SQLite connection fields, mutex subsystem, benign malloc regions, `sqlite3_log()` via error handling, and shared-cache lock conflict paths. It sets database error state through `sqlite3ErrorWithMsg()`.

Risks: callbacks are invoked while `STATIC_MAIN` is still held in this implementation, so callback behavior must respect SQLite's documented restrictions and avoid deadlock-prone reentry. OOM while growing the callback argument array intentionally degrades into multiple smaller callback invocations to avoid lost notifications. Deadlock detection follows only `pUnlockConnection` chains; wrong maintenance of those fields would miss or falsely report deadlocks.

Test signals: enable unlock-notify and shared cache; create two or more blocked connections and verify callback grouping; test immediate notification after blocker release; create deadlock cycles and expect `SQLITE_LOCKED`; simulate OOM during callback argument growth; and close a blocking connection while waiters are registered.
