<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/brlock.c -->
# sources/user-network-fs/samba/source3/locking/brlock.c

## Purpose
`brlock.c` implements Samba's byte-range lock service on top of `brlock.tdb`. It replaces direct `fcntl`-only behavior with a database-backed model that can emulate Windows byte-range semantics, POSIX byte-range semantics, durable-handle disconnect/reconnect behavior, and optional mapping to kernel POSIX locks.

## Important APIs, Types, And Functions
The private `struct byte_range_lock` carries the current `files_struct`, optional request memory/GUID context, the in-memory `struct lock_struct` array, a modified bit, and the locked `db_record`. Public entry points include `brl_init`, `brl_shutdown`, `brl_get_locks`, `brl_get_locks_readonly`, `brl_lock`, `brl_unlock`, `brl_locktest`, `brl_lockquery`, `brl_close_fnum`, `brl_mark_disconnected`, `brl_reconnect_disconnected`, `brl_cleanup_disconnected`, `share_mode_do_locked_brl`, and `file_has_brlocks`. Key helpers are `byte_range_valid`, `byte_range_overlap`, `brl_conflict`, `brl_conflict_posix`, `brl_conflict_other`, `brlock_posix_split_merge`, and `byte_range_lock_flush`.

## Control Flow
Writers call `brl_get_locks`, which fetches and chain-locks a `brlock.tdb` record keyed by `struct file_id`; freeing the returned talloc object flushes changes and releases the record. Windows locks check overlap conflicts, prune dead pids opportunistically, optionally set lower POSIX locks through `set_posix_lock_windows_flavour`, append one `lock_struct`, and mark modified. POSIX-flavour locks rebuild the array through split/merge logic so same-context overlapping ranges coalesce or replace as POSIX semantics require, then optionally map directly to kernel locks. Unlock paths mirror this: Windows unlock removes an exact lock, while POSIX unlock may split retained ranges. `share_mode_do_locked_brl` runs a callback with a share-mode g-lock held and a read-only byte-range snapshot that can be upgraded and flushed afterward.

## State And Persistence
`brlock.tdb` is a volatile TDB opened with `TDB_SEQNUM` and lock order 2. Keys are raw `struct file_id`; values are raw arrays of `struct lock_struct`, not NDR. `byte_range_lock_flush` deletes empty records, stores non-empty arrays with `TDB_REPLACE`, and removes entries whose pid was marked zero after dead-server detection. Read-only lookups cache `fsp->brlock_rec` until the database sequence number changes. Durable-handle disconnects rewrite lock pids/tids/fnums to disconnected sentinels; reconnect restores them to the current server id and handle.

## Dependencies And Integration Points
This file depends on dbwrap/TDB, Samba server ids, messaging context, VFS byte-range lock hooks (`SMB_VFS_BRL_LOCK_WINDOWS`, `SMB_VFS_BRL_UNLOCK_WINDOWS`), POSIX mapping functions from `posix.c`, share-mode locking from `share_mode_lock.c`, and oplock contention accounting. It is invoked by `locking.c` request wrappers and by close/durable-handle paths in smbd.

## Risks And Test Signals
The raw on-disk value format is ABI-sensitive to `struct lock_struct` layout and endian assumptions. Range math is delicate around zero-length locks and `UINT64_MAX` overflow; Windows and POSIX semantics intentionally differ. Destructor-driven flush makes talloc lifetime correctness part of the locking protocol. Stale-pid cleanup mutates records during conflict checks, so tests need multi-process death scenarios. Good test signals include SMB byte-range lock torture tests, zero-length and wraparound ranges, same-context read/write stacking, POSIX split/merge cases, durable disconnect/reconnect cleanup, lock waiter wakeups, and operation with `lp_posix_locking` both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/brlock.c -->
