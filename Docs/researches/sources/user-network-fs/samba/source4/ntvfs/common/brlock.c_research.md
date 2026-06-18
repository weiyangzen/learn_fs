# sources/user-network-fs/samba/source4/ntvfs/common/brlock.c

## Purpose

`brlock.c` is the backend-dispatch wrapper for source4 NTVFS byte-range locking. It exposes the public brlock API while delegating implementation to a selected `struct brlock_ops`, defaulting to the TDB backend.

## Important APIs, Types, and Functions

Public functions are `brlock_set_ops()`, `brlock_init()`, `brlock_create_handle()`, `brlock_lock()`, `brlock_unlock()`, `brlock_remove_pending()`, `brlock_locktest()`, `brlock_close()`, and `brlock_count()`. The global static `ops` points at the active backend.

## Control Flow

`brlock_init()` initializes the default TDB ops via `brl_tdb_init_ops()` if no backend has been installed, then calls `ops->brl_init()`. All other functions are thin pass-throughs to the corresponding backend method.

## State and Persistence Behavior

The only state in this file is the process-global backend ops pointer. Persistent lock state is owned by the backend, normally `brlock_tdb.c` using a temporary cluster DB.

## Dependencies and Integration Points

It depends on `ntvfs_common.h`, messaging, IRPC, cluster helpers, and loadparm types through the backend interface. NTVFS disk backends use this API to create lock contexts and handles for open files.

## Risks and Edge Cases

The process-global `ops` is mutable and not synchronized; test or alternate backend injection must happen before concurrent use. There are no NULL checks in pass-through calls after initialization, so backend installation must be complete and correct.

## Test Signals

Tests should verify default TDB backend selection, alternate backend injection through `brlock_set_ops()`, and that public API calls dispatch exactly once to the expected ops.
