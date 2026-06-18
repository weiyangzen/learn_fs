# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/userdlm.c

## Purpose

Implements the kernel-side lock protocol used by `ocfs2_dlmfs`. It wraps OCFS2 cluster locking APIs with a small userspace-facing lock-resource state machine for PR/EX locks, LVB handling, BAST-driven downconversion, holder counting, cancellation, and teardown.

## Major Responsibilities

- Maintain `struct user_lock_res` state.
- Register an OCFS2 locking protocol for dlmfs.
- Handle lock AST, BAST, and unlock AST callbacks.
- Acquire and release locks for file open/close.
- Track local PR/EX holders.
- Downconvert locks when blocked by other nodes.
- Cancel in-progress upconverts when needed.
- Read/write lock value blocks.
- Destroy locks safely during unlink/eviction.
- Register/unregister cluster connections.

## Lock State

`user_lock_res` tracks:

- current granted level: `l_level`
- requested level: `l_requested`
- blocking level: `l_blocking`
- flags: attached, busy, blocked, teardown, queued, cancel
- PR holder count: `l_ro_holders`
- EX holder count: `l_ex_holders`
- OCFS2 DLM lock status block: `l_lksb`
- lock name
- wait queue
- work item

Only EX, PR, NL, and IV semantics are expected here. Comments explicitly warn that `user_highest_compat_lock_level()` would need updates if more lock levels were supported.

## Locking Protocol Callbacks

`user_dlm_lproto` registers:

- `user_ast`
- `user_bast`
- `user_unlock_ast`

`user_dlm_set_locking_protocol()` publishes the maximum supported protocol version through stackglue.

## AST Handling

`user_ast()` runs when a lock request or conversion completes.

It:

- Checks DLM status.
- Verifies requested mode is not IV.
- If downconverting, clears blocked state when the new requested level is compatible with the blocking request.
- Updates current level to requested level.
- Resets requested level to IV.
- Marks the lock attached.
- Clears busy.
- Wakes waiters.

## BAST Handling

`user_bast()` runs when another node is blocked by this lock.

It:

- Sets `USER_LOCK_BLOCKED`.
- Raises `l_blocking` if the new blocking level is higher.
- Queues the lock resource for asynchronous downconversion.
- Wakes waiters so poll users can observe the blocked state.

`__user_dlm_queue_lockres()` takes an inode reference and queues `user_dlm_unblock_lock()` on `user_dlm_worker`.

## Unlock AST Handling

`user_unlock_ast()` handles completion of unlock or cancel.

Cases:

- Teardown unlock: sets current level to IV.
- Cancel returned `DLM_CANCELGRANT`: cancel lost the race; clear cancel flag but leave busy handling to the normal AST.
- Cancel succeeded: reset requested level to IV, clear cancel flag, and requeue if still blocked.

It clears busy when appropriate and wakes waiters.

## Downconversion Worker

`user_dlm_unblock_lock()` processes BAST-driven downconversion.

It:

1. Clears queued flag.
2. Exits if no longer blocked or teardown is active.
3. If busy and not already canceling, sends `DLM_LKF_CANCEL`.
4. If local holders still conflict with the blocking request, exits.
5. Computes the highest compatible downconvert level.
6. Marks the lock busy and requested.
7. Sends `ocfs2_dlm_lock()` with `DLM_LKF_CONVERT | DLM_LKF_VALBLK`.
8. Recovers busy state on error.
9. Drops the inode ref taken when queued.

This worker is the bridge between asynchronous BAST notification and later lock-level reduction.

## Acquiring Locks

`user_dlm_cluster_lock()` is called from dlmfs file open.

It validates requested level is EX or PR, then loops until the lock can be held or an error occurs.

It handles:

- pending signals: returns `-ERESTARTSYS`
- teardown: returns `-EAGAIN`
- busy upconvert: waits if caller needs a higher level
- blocked incompatible state: waits for blocked state to clear
- lock upgrade from IV/lower level: calls `ocfs2_dlm_lock()`
- noqueue failure: propagates `-EAGAIN`
- successful local reuse: increments holder count

It waits on `USER_LOCK_BUSY` after submitting an async DLM lock request, then rechecks state.

## Releasing Locks

`user_dlm_cluster_unlock()` is called from dlmfs file close.

It:

- Validates level.
- Decrements the corresponding holder count.
- Conditionally queues downconversion if the lock is blocked and remaining holders no longer conflict.

It does not necessarily unlock from the cluster immediately; the lock can remain cached/downconverted according to BAST pressure.

## LVB Handling

`user_dlm_write_lvb()`:

- Requires current level at least EX.
- Copies caller bytes into the DLM LVB.

`user_dlm_read_lvb()`:

- Requires current level at least PR.
- Returns false if the LVB is not valid.
- Otherwise copies `DLM_LVB_LEN` bytes to caller.

## Lock Initialization And Destruction

`user_dlm_lock_res_init()` initializes spinlock, wait queue, IV levels, and lock name.

`user_dlm_destroy_lock()`:

- Sets teardown state.
- Waits for busy operations to finish.
- Fails with `-EBUSY` if PR/EX holders remain.
- If no DLM lock was ever attached, leaves teardown set and succeeds.
- Otherwise marks busy and calls `ocfs2_dlm_unlock()` with `DLM_LKF_VALBLK`.
- Waits for unlock AST to clear busy.
- Clears teardown/busy on unlock submission error.

This is used by unlink and inode eviction.

## Cluster Connection

`user_dlm_register()` connects to an OCFS2 cluster domain with `ocfs2_cluster_connect_agnostic()` using the dlmfs protocol and a no-op recovery handler.

`user_dlm_unregister()` disconnects with `ocfs2_cluster_disconnect()`.

The recovery handler is intentionally no-op because dlmfs ignores recovery events at this layer.

## Concurrency

- `l_lock` protects all user lock state.
- `l_event` wakes waiters for busy/blocked changes.
- Workqueue downconversion takes an inode reference to keep the lock resource alive.
- `USER_LOCK_QUEUED` prevents duplicate queued work.
- `USER_LOCK_IN_CANCEL` disambiguates cancel unlock ASTs from teardown unlock ASTs.

## Dependencies

- OCFS2 stackglue cluster lock API.
- `dlmfs.c` inode private structure.
- Linux workqueues, wait queues, spinlocks, and signal checking.
- OCFS2 locking protocol version definitions.

## Research Notes

`userdlm.c` is a compact caching lock manager for dlmfs userspace handles. Opens increment local holder counts and may upconvert the cluster lock; closes decrement holder counts and may permit async downconversion. BASTs drive poll visibility and eventual downconversion, preserving LVB state through conversion and teardown.
