# sources/user-network-fs/samba/source4/ntvfs/common/brlock_tdb.c

## Purpose

`brlock_tdb.c` implements the TDB-backed byte-range locking service for source4 NTVFS. It stores locks in a cluster-capable temporary DB keyed by a file identity blob and emulates Windows/NT byte-range locking semantics, including pending locks and retry notifications.

## Important APIs, Types, and Functions

Backend ops are registered by `brl_tdb_init_ops()`. Internal types include `struct brl_context`, `struct lock_context`, `struct lock_struct`, and `struct brl_handle`. Important functions include `brl_tdb_init()`, `brl_tdb_create_handle()`, `brl_tdb_lock()`, `brl_tdb_unlock()`, `brl_tdb_remove_pending()`, `brl_tdb_locktest()`, `brl_tdb_close()`, `brl_tdb_count()`, `brl_tdb_conflict()`, `brl_tdb_conflict_other()`, `brl_tdb_overlap()`, and notification helpers.

## Control Flow

Init opens the `brlock` cluster temp DB. Each lock operation fetches and locks the file-key record, validates the range, builds a `lock_struct`, checks conflicts against existing serialized locks, appends on success, and stores the updated array. Pending locks first attempt the real read/write lock while holding the record lock to avoid a race, then store a pending entry if the real lock cannot be granted. Unlock finds an exact matching write lock first, then any non-pending matching lock, removes it, notifies overlapping pending locks, and stores or deletes the record. Close removes all locks for the handle and notifies pending holders.

## State and Persistence Behavior

Persistent runtime state is in `brlock.tdb` records whose values are linear arrays of `struct lock_struct`. Handles cache the file key, NTVFS handle, and last failed lock to reproduce Windows error-code behavior. Pending locks store `notify_ptr` and target server ID for `MSG_BRL_RETRY` imessaging notifications.

## Dependencies and Integration Points

It depends on dbwrap, cluster DB helpers, imessaging, NTVFS handles, generated lock enums, and loadparm. NTVFS file backends use it through `brlock.c` for SMB lock/unlock/read/write conflict checks.

## Risks and Edge Cases

The record value stores raw structs, including pointers, so it is suited to Samba runtime temp DB use and same-binary interpretation, not durable cross-version storage. Stale process detection is a TODO, so locks from dead servers may persist until cleanup semantics elsewhere handle them. `brl_tdb_notify_all()` checks `locks->lock_type` instead of `locks[i].lock_type`, which looks suspicious. Error-code compatibility for repeated failed locks is intentionally subtle. Wrapped 64-bit lock ranges are rejected.

## Test Signals

Tests should cover read/read sharing, write conflicts, same-context exceptions, invalid wrapped ranges, pending lock retry notification, unlock exact-match rules, close cleanup, count, SMB1 versus SMB2 error-code differences, high-offset conflict behavior, and dead/stale lock scenarios in clustered setups.
