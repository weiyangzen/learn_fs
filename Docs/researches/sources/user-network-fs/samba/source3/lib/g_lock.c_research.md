# sources/user-network-fs/samba/source3/lib/g_lock.c

Purpose: implements process-global read/write/update locks on top of watched dbwrap records, with data payloads, process-death cleanup, async waiting, and watcher wakeups.

Important APIs/types/functions: context init, `g_lock_lock[_send]/recv()`, `g_lock_unlock()`, data write/watch/dump APIs, lock-list traversal, callback helpers, and internal `struct g_lock`.

Control flow: lock acquisition parses the record, handles exclusive/shared/upgrade/downgrade cases, stores ownership, or queues a dbwrap watcher and retries after wakeup/timeout. Unlock removes ownership, advances the lock epoch, and wakes waiters. Data writes require exclusive ownership and advance the data epoch; data-watchers loop until that epoch changes.

State/persistence behavior: each record stores exclusive server id, lock/data epochs, shared holder array, and optional data. Default backend is volatile `g_lock.tdb`; custom backends are wrapped with watched dbwrap. Dead holders are pruned through server-id existence checks.

Dependencies/integration: depends on dbwrap watch, messaging, server-id helpers, lock-order instrumentation, TDB utilities, and tevent. `test_g_lock.c` exercises the core behavior.

Risks/test signals: correctness depends on epoch fairness, reliable cleanup, non-reentrant `ctx->busy`, and watcher ordering. Tests should stress contention, upgrades, stale processes, callbacks, data changes, timeouts, and lock-order accounting.
