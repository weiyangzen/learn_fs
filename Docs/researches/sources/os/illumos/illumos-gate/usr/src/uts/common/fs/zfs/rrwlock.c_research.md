# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/rrwlock.c

This file implements ZFS re-entrant reader/writer locks (`rrwlock_t`) and reader-mostly locks (`rrmlock_t`). The core `rrwlock_t` behaves like a reader/writer lock, but permits a thread that already holds a read lock to acquire another read hold even when writers are waiting.

Core responsibilities:
- Maintains per-thread read-lock tracking with TSD nodes (`rrw_node_t`) only when needed for re-entrant detection or when `track_all` is enabled.
- Tracks anonymous readers with `rr_anon_rcount` on the normal fast path, and linked readers with `rr_linked_rcount` when writers are pending or all readers must be tracked.
- Provides initialization, teardown, generic enter, read enter, priority read enter, write enter, exit, and held-state queries for `rrwlock_t`.
- Gives waiting writers priority over new non-reentrant readers once anonymous readers have drained.
- Allows explicit priority read acquisition through `rrw_enter_read_prio()` for cross-thread cases where normal per-thread reentrancy detection cannot prove the relationship.
- Uses `rrw_tsd_destroy()` to panic if a thread exits while still carrying rrw TSD state.
- Implements `rrmlock_t` as an array of `rrwlock_t` instances to reduce read-side contention by hashing readers across locks while making writers acquire every underlying lock.

Important control-flow notes:
- `rrw_enter_read_impl()` is the central read acquisition path. It has a kernel non-debug fast path that increments `rr_anon_rcount` directly when no writer is active/wanted and `track_all` is false.
- If a writer is waiting while anonymous readers still exist, new readers are allowed because they might be re-entrant readers that cannot yet be identified. Once anonymous readers drain, only tracked re-entrant readers or priority readers may bypass a waiting writer.
- `rrw_enter_write()` sets `rr_writer_wanted` while waiting for anonymous readers, linked readers, and any current writer to clear, then records `curthread` as the owner.
- `rrw_exit()` removes linked TSD state when present, otherwise drops anonymous reader state, or clears the writer owner. It broadcasts waiters when the relevant count reaches zero or a writer exits.
- `rrw_held(RW_READER)` is exact only when `track_all` is enabled; otherwise anonymous readers mean it may return true because some thread holds a read lock.
- `rrm_enter_read()` hashes `curthread` to one underlying lock, while `rrm_enter_write()` serially acquires all underlying locks. `rrm_exit()` releases all locks for a writer or the hashed lock for a reader.

Key dependencies:
- ZFS refcount helpers for reader accounting and tagged debug tracking.
- Illumos mutexes, condition variables, TSD APIs, and `curthread`.
- `rrwlock.h` / `rrmlock_t` definitions, including `RRM_NUM_LOCKS`.

Risk-sensitive invariants:
- Writers are not re-entrant and cannot be acquired while the current thread already owns the writer side.
- Read-to-write or write-to-read lock upgrades are not supported by this implementation.
- TSD nodes must be added and removed in balance with linked reader refcounts; a leaked node causes thread-exit panic.
- `rrmlock_t` read locks must be released by the same thread that acquired them because the hash is based on `curthread`.
