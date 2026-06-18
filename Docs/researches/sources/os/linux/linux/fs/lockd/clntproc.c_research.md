# File Research: sources/os/linux/linux/fs/lockd/clntproc.c

Purpose: Implements client-side NLM TEST, LOCK, UNLOCK, CANCEL, reclaim, async RPC handling, lockowner tracking, and status-to-errno conversion.

Key functionality:
- Generates NLM cookies with an atomic counter.
- Maps VFS `fl_owner_t` to stable 32-bit NLM pseudo-pids via `struct nlm_lockowner`.
- `nlmclnt_proc()` is the main fcntl-style entry point for GETLK/SETLK/SETLKW/UNLCK.
- `nlmclnt_call()` performs synchronous RPC with grace-period retry/rebind handling.
- Async helpers support unlock/cancel/reply RPCs and task callbacks.
- `nlmclnt_lock()` handles local VFS precheck, remote lock request, blocking wait/poll loop, cancellation, reboot state check, and final local lock installation.
- `nlmclnt_unlock()` removes the local lock then sends async remote unlock.
- `nlmclnt_reclaim()` reissues reclaim LOCK calls during recovery.
- `nlm_stat_to_errno()` maps NLM wire statuses to Linux errno values.

Dependencies and integration:
- Uses NFS file credentials and file handles, host bind/rebind, NSM monitor state, VFS file-lock APIs, and tracepoints.
- Cooperates with `clntlock.c` for blocking wait queues and with `host.c` for recovery state.

Risk notes:
- Blocking lock handling is intentionally defensive against servers that return BLOCKED without later callbacks.
- Fatal/interrupted blocking paths attempt CANCEL and may send remote UNLOCK cleanup.
- Lockowner lifetime is tied to file lock private ops; missed release would leak host refs.
- Grace-period and reboot-state races are handled by retrying when host state changes.
