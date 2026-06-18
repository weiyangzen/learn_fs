# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmlock.c

## Purpose
Implements the public OCFS2 DLM lock acquisition API and the network handler for remote lock creation.

## Main Entry Points
- `dlmlock()` is the exported API for lock and convert requests.
- `dlm_create_lock_handler()` handles `DLM_CREATE_LOCK_MSG` on the master node.
- `dlm_new_lock()`, `dlm_lock_get()`, `dlm_lock_put()`, and `dlm_lock_attach_lockres()` manage lock allocation, references, and lock-resource attachment.
- `dlm_init_lock_cache()` / `dlm_destroy_lock_cache()` manage the lock slab cache.

## Lock Acquisition
For new locks, `dlmlock()` validates mode/flags/name, allocates a node-local cookie, creates a `struct dlm_lock`, waits for recovery unless this is a recovery lock, obtains or masters the lock resource through `dlm_get_lock_resource()`, and then calls either `dlmlock_master()` or `dlmlock_remote()`.

`dlmlock_master()` grants immediately if compatible with granted and converting queues. Otherwise it returns `DLM_NOTQUEUED` for `LKM_NOQUEUE` or queues the lock on `blocked`. Granted locks reserve/queue ASTs except for the special `$RECOVERY` lock.

`dlmlock_remote()` places the lock on the local secondary blocked queue, marks `lock_pending`, sends `DLM_CREATE_LOCK_MSG`, and reverts on failure. `$RECOVERY` has special handling because it may be granted without a later AST.

## Conversion Path
When `LKM_CONVERT` is set, `dlmlock()` validates that the caller passed the original `lksb`, AST, BAST, and AST data. It then retries `dlmconvert_master()` or `dlmconvert_remote()` through recovery/migration/forward statuses.

## Remote Create Handler
`dlm_create_lock_handler()` validates domain state, lock name length, allocates a remote-node lock and kernel-owned LKSB, applies `LKM_GET_LVB`, looks up the lock resource, rejects non-normal lockres state, attaches the lock to the resource, and invokes `dlmlock_master()`.

## Reference and Cookie Model
Cookies combine the node number in the top byte with a per-node 56-bit sequence protected by `dlm_cookie_lock`. Lock release asserts the lock is off all queues and AST/BAST lists before detaching the lock resource and freeing any kernel-allocated LKSB.
