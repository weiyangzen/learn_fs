# sources/user-network-fs/samba/source4/ntvfs/common/opendb.c

## Purpose

`opendb.c` is the backend-dispatch wrapper for source4 NTVFS open-file database services. It exposes public APIs for share-mode checks, open registration, close cleanup, pending-open notifications, delete-on-close, write-time tracking, and oplock management.

## Important APIs, Types, and Functions

Public functions include `odb_set_ops()`, `odb_init()`, `odb_lock()`, `odb_get_key()`, `odb_can_open()`, `odb_open_file()`, `odb_open_file_pending()`, `odb_close_file()`, `odb_remove_pending()`, `odb_rename()`, `odb_get_path()`, `odb_set_delete_on_close()`, `odb_set_write_time()`, `odb_get_file_infos()`, `odb_update_oplock()`, and `odb_break_oplocks()`.

## Control Flow

Like `brlock.c`, `odb_init()` installs default TDB ops via `odb_tdb_init_ops()` if no backend is selected, then delegates. All other functions pass through to the active backend. The intended calling flow is explicit in comments: callers lock a file key with `odb_lock()`, call `odb_can_open()`, then call `odb_open_file()` with the same lock handle if opening is permitted.

## State and Persistence Behavior

This file stores only a process-global `struct opendb_ops *ops`. Persistent open-file state is owned by the backend, normally `opendb_tdb.c` using `openfiles` cluster temp DB records.

## Dependencies and Integration Points

It depends on NTVFS contexts, cluster IDs, loadparm, and `ntvfs_common.h`. Disk backends use this wrapper to coordinate open/share semantics across server instances.

## Risks and Edge Cases

The global backend pointer is mutable without synchronization. Since pass-throughs do not guard against NULL after initialization, alternate backend tests must set a complete ops table. The protocol contract requiring `odb_can_open()` before `odb_open_file()` is enforced by the backend, not the wrapper.

## Test Signals

Tests should verify default backend selection, alternate ops injection, dispatch for every wrapper, and enforcement of the can-open-before-open sequence through the TDB backend.
