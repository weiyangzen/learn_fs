# File Research: sources/os/linux/linux-stable/fs/lockd/clntproc.c

Implements client-side NLM RPC procedure orchestration for test, lock, unlock, cancel, and reclaim.

Key logic:
- `nlmclnt_next_cookie()` creates 4-byte cookies from an atomic counter.
- Lock owners map VFS `fl_owner_t` to per-host synthetic 32-bit pids with refcounted `nlm_lockowner` objects.
- `nlmclnt_setlockargs()` copies NFS file handle, caller name, owner handle, pid, range, and lock type into RPC args.
- `nlmclnt_proc()` is the exported fcntl-style entry point; it allocates a request, initializes private lock state, dispatches GETLK/SETLK/SETLKW/UNLCK, then releases private state.

RPC behavior:
- `nlmclnt_call()` performs synchronous RPC with grace-period waiting, rebinds after connection failures, and wakes grace waiters when the server leaves grace.
- `__nlm_async_call()`, `nlm_async_call()`, and `nlm_async_reply()` launch async RPC tasks.
- `nlmclnt_async_call()` starts async work but waits for completion to track local lock state.

Lock operations:
- `nlmclnt_test()` maps conflict results back into the caller’s `file_lock`.
- `nlmclnt_lock()` monitors peer state, locally preflights with `FL_ACCESS`, queues a wait block before RPC to catch early GRANTED callbacks, polls blocked locks, cancels interrupted blocking requests, installs granted locks locally, and unlocks remotely/local state on fatal errors.
- `nlmclnt_reclaim()` sends reclaim LOCK during server grace.
- `nlmclnt_unlock()` removes local lock state first, then sends async UNLOCK and handles expected status.
- `nlmclnt_cancel()` sends async CANCEL with bounded retry logic.

Status mapping:
- `nlm_stat_to_errno()` maps NLM statuses to Linux errno, including v4-only deadlock, read-only filesystem, stale fh, and overflow cases.
