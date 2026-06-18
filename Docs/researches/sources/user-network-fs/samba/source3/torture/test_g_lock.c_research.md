# sources/user-network-fs/samba/source3/torture/test_g_lock.c

Purpose: This file is a broad torture suite for Samba's global lock (`g_lock`) API. It covers basic lock/unlock semantics, lock data storage, read/write upgrade behavior, interprocess contention, stale lock cleanup, upgrade deadlock detection, data watch notification, and a ping-pong performance pattern.

Important APIs/types/functions: `get_g_lock_ctx()` obtains global tevent and messaging contexts and creates a `g_lock_ctx`. Public entrypoints include `run_g_lock1()` through `run_g_lock8()` plus `run_g_lock_ping_pong()`. Key APIs are `g_lock_lock()`, `g_lock_lock_send()/recv()`, `g_lock_unlock()`, `g_lock_write_data()`, `g_lock_dump()`, and `g_lock_watch_data_send()`. Parser callbacks validate exclusive/shared lockers and stored data.

Control flow: Simple tests run in-process: double-write lock returns `NT_STATUS_WAS_LOCKED`, unlocking an absent lock returns `NT_STATUS_NOT_FOUND`, writing data requires a held write lock, and read locks upgrade to write locks. Contention tests fork children holding read or write locks, coordinate with pipes, then verify immediate timeouts, async acquisition after child exit, and dump contents. Cleanup tests fork children that exit while holding locks to check heuristic removal of stale server ids. Deadlock testing arranges two readers attempting upgrade and expects `NT_STATUS_POSSIBLE_DEADLOCK`. The watch test starts a data watch, writes nonempty then empty data under a write lock, unlocks, and polls the watch.

State/persistence behavior: Lock state is stored in the g_lock backend and includes exclusive locker, shared locker array, and optional data bytes. Tests rely on process identity from messaging server ids and fork reinitialization via `reinit_after_fork()`. Some locks are intentionally stale after child exit to exercise cleanup.

Dependencies and integration points: Dependencies include source3 messaging, server id utilities, sys read/write wrappers, TDB utilities, tevent NTSTATUS helpers, and global contexts. The suite validates global locking used by clustered and multi-process Samba subsystems.

Risks: Fork/pipe synchronization and process liveness checks are inherently timing sensitive. The tests assume specific NTSTATUS behavior for conflicts, upgrades, and stale cleanup. Clustered mode lacks clear-if-first semantics, so `run_g_lock6()` explicitly wipes stale lock state before starting.

Test signals: Passing emits expected statuses for all lock transitions: OK, `WAS_LOCKED`, `NOT_FOUND`, `NOT_LOCKED`, `IO_TIMEOUT`, `POSSIBLE_DEADLOCK`, and successful async completion. Dump parser callbacks verify the exact locker identity and number of locks.
