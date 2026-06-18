# File Research: sources/teaching/minix/minix/servers/vfs/tll.c

## Purpose
Implements the VFS three-level lock used by vnode and vmnt objects.

## Lock Modes
- `TLL_READ`: shared read-only access.
- `TLL_READSER`: serialized read access with an owner, allowing concurrent read-only holders.
- `TLL_WRITE`: exclusive write access.
- `TLL_NONE`: unlocked.

## Main Operations
- `tll_init()` initializes lock state and queues.
- `tll_lock()` grants or queues requested access.
- `tll_unlock()` releases access and wakes queued owners.
- `tll_upgrade()` upgrades read-serialized to write-only after readers drain.
- `tll_downgrade()` downgrades write to read-serialized or read-serialized to read-only.
- `tll_islocked()`, `tll_locked_by_me()`, `tll_haspendinglock()` expose lock state.

## Queueing Model
There are two queues:
- `t_write` for write and read-only requests.
- `t_serial` for read-serialized requests.

The implementation is write-biased: if write requests are pending, new read/read-serialized requests queue instead of bypassing. Threads sleep and wake through `worker_wait()` and `worker_signal()`.

## Upgrade/Downgrade Behavior
`TLL_UPGR` marks a read-serialized owner waiting for read-only holders to leave before becoming write-only. `TLL_PEND` marks that a selected owner has been signaled but has not yet resumed and taken its mode. Downgrade can allow a queued read-serialized owner to proceed when no write queue exists.

## Dependencies
Relies on global `self`, `struct worker_thread`, worker wait/signal APIs, and assertions. It is included indirectly by vnode/vmnt lock wrappers.

## Risks and Notes
The lock is non-reentrant for owned modes and returns `EBUSY` when the same worker already owns it. Correctness depends on a worker not being enqueued twice and on `w_next` being reset when ownership changes.
