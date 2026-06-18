# File Research: sources/os/linux/linux/fs/lockd/svclock.c

## Purpose
`svclock.c` is the server-side lock state engine for lockd, especially blocked locks. It bridges NLM requests to VFS byte-range locks, manages blocked request lists, handles VFS lock-manager callbacks, sends GRANTED callbacks to clients, processes GRANTED_RES replies, and owns lockowner reference lifetime for remote NLM lock owners.

## Main Responsibilities
- Maintains the global `nlm_blocked` retry list guarded by `nlm_blocked_lock`.
- Creates, inserts, removes, and frees `struct nlm_block` entries representing blocked NLM lock requests.
- Maintains per-file blocked request lists through each `nlm_file`'s `f_blocks`.
- Allocates and tracks NLM lock owners (`struct nlm_lockowner`) per remote host and PID.
- Implements `nlmsvc_lock()`, `nlmsvc_testlock()`, `nlmsvc_unlock()`, and `nlmsvc_cancel_blocked()`.
- Provides `nlmsvc_lock_operations`, the VFS lock manager callbacks used for asynchronous lock grants and owner refcounting.
- Retries deferred or blocked locks from the lockd service thread through `nlmsvc_retry_blocked()`.
- Dispatches GRANTED callbacks and processes GRANTED_RES responses.

## Key Data Structures
- `nlm_blocked`: global ordered list of blocked locks, ordered by retry time except `NLM_NEVER` entries.
- `struct nlm_block`: contains file, host, daemon, grant call, retry timing, deferred request state, flags, and kref.
- `struct nlm_rqst`: allocated for callback RPCs and used by blocks as grant-call state.
- `struct nlm_lockowner`: host-scoped owner object used as VFS `flc_owner` for lockd POSIX locks.

## Control Flow
`nlmsvc_lock()` checks whether the file can be locked, determines whether async locking is supported, obtains or creates a matching `nlm_block`, handles deferred retry states, validates grace/reclaim rules, inserts the block, and calls `vfs_lock_file()`. It maps VFS outcomes to NLM statuses: success removes the block, `-EAGAIN` yields denied or blocked depending on wait/async state, `FILE_LOCK_DEFERRED` creates a deferred RPC revisit, `-EDEADLK` maps to an internal deadlock status, and other errors map to denied-no-locks.

`nlmsvc_grant_deferred()` and `nlmsvc_notify_blocked()` are callbacks from the VFS/filesystem lock layer. They find the corresponding block, update grant/timed-out flags when necessary, move it to the retry head, and wake lockd.

`nlmsvc_retry_blocked()` walks due entries from `nlm_blocked`. Deferred queued requests are revisited through the RPC cache deferral callback. Blocking locks are retried by `nlmsvc_grant_blocked()`, which attempts the VFS lock again and, on success, sends an async `NLMPROC_GRANTED_MSG` callback.

`nlmsvc_grant_reply()` handles a client's GRANTED_RES: grace-period denial schedules a retry, denial unlocks the already granted VFS lock, and other statuses remove the block.

## Integration Points
- Calls VFS locking APIs from `fs/locks.c`: `vfs_lock_file()`, `vfs_test_lock()`, `vfs_cancel_lock()`, `locks_delete_block()`, `locks_copy_lock()`, and `locks_release_private()`.
- Exposes `nlmsvc_lock_operations` so VFS lock code can call back into lockd.
- Uses SUNRPC client helpers for async GRANTED_MSG callbacks.
- Uses `nlmsvc_file_file()` / `nlmsvc_file_inode()` file helpers supplied elsewhere in lockd.

## Concurrency and Lifetime Notes
- Global blocked-list operations use `nlm_blocked_lock`.
- Per-file state changes generally use `file->f_mutex`; kref destruction uses `kref_put_mutex()` so final block freeing can safely unlink from the file list.
- `nlmsvc_create_block()` increments the file reference count and `nlmsvc_free_block()` releases it through `nlm_release_file()`.
- The comments explicitly acknowledge races where RPC callbacks can move entries while the service thread traverses the global list; the design tolerates duplicate visits.

## Risks and Edge Cases
- The code is race-sensitive because VFS grant callbacks, RPC callbacks, CANCEL, UNLOCK, and service retries can all act on the same block.
- `nlmsvc_grant_release()` is noted as problematic because it can call `nlmsvc_release_block()` from an RPC release callback even though that can grab a mutex.
- Deferred nonblocking locks rely on RPC cache deferral/revisit hooks and can time out if no VFS callback arrives.
- The implementation intentionally preserves compatibility behavior around GRANTED cookies and client callback quirks.
