# File Research: sources/os/linux/linux-stable/fs/lockd/svclock.c

## Summary
Server-side lock state and blocked-lock retry machinery. This is the main race-prone lockd file: it manages pending blocks, lock owners, VFS async lock callbacks, deferred RPC revisits, GRANTED_MSG retransmission, and GRANTED_RES cleanup.

## Main APIs
- `nlmsvc_lock()`, `nlmsvc_testlock()`, `nlmsvc_unlock()`, `nlmsvc_cancel_blocked()`.
- `nlmsvc_retry_blocked()` drives retry and deferred-request processing from the lockd thread.
- `nlmsvc_grant_reply()` handles client `GRANTED_RES`.
- `nlmsvc_locks_init_private()` and `nlmsvc_release_lockowner()` manage NLM lock owners.
- `nlmsvc_lock_operations` supplies VFS lock-manager callbacks.

## Behavior
Blocking lock requests are represented by `struct nlm_block` on a global time-ordered `nlm_blocked` list and on each file’s block list. If VFS grants immediately, the block is removed. If VFS blocks or defers, lockd stores the request, sleeps or drops the RPC reply, and later sends a `GRANTED_MSG` callback. Client acceptance removes the block; denial unlocks the VFS lock.

## State and Synchronization
`nlm_blocked_lock` protects the global retry list and many block transitions. `file->f_mutex` protects per-file block list teardown. `kref` controls block lifetime. Lock owners are refcounted under `host->h_lock` and are also managed by VFS `lm_get_owner` / `lm_put_owner`.

## Dependencies
Generic VFS locks (`vfs_lock_file()`, `vfs_test_lock()`, `vfs_cancel_lock()`), SunRPC async calls, lockd file and host reference APIs, and the global retry timer in `svc.c`.

## Risks
GRANT, CANCEL, UNLOCK, deferred filesystem callbacks, and RPC completion can cross in flight. `nlmsvc_grant_release()` notes it calls a mutex-taking release path from RPC release context. List movement can cause repeated traversal, which comments accept as benign. Correct lock-owner refcounting is critical because copied VFS locks can retain owners.
