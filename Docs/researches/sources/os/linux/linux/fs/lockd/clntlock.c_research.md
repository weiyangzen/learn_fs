# File Research: sources/os/linux/linux/fs/lockd/clntlock.c

Purpose: Client-side lock blocking, grant callback matching, NFS mount initialization/cleanup, and lock reclaim after server reboot.

Key functionality:
- `nlmclnt_init()` starts lockd, finds/binds an NLM host, and installs client callbacks.
- `nlmclnt_done()` releases the host and decrements lockd service usage.
- Maintains global `nlm_blocked` wait list protected by `nlm_blocked_lock`.
- `nlmclnt_grant()` matches GRANTED callbacks by range, owner pid, remote address, and file handle, then wakes waiting lockers.
- `nlmclnt_recovery()` spawns a reclaim thread per host reboot.
- `reclaimer()` rebinds the host, reclaims granted locks, handles repeated reboot state changes, and wakes blocked waiters with grace-period status.

Dependencies and integration:
- Uses `lockd_up/down`, host lookup/bind/release from `host.c`, and reclaim RPC from `clntproc.c`.
- Compares file handles through NFS helpers and emits tracepoints.

Risk notes:
- Grant matching explicitly avoids using cookies because servers do not reliably echo the original blocking request cookie.
- Reclaimer uses host `h_rwsem` to serialize recovery against normal lock operations.
- Failed reclaimer thread creation leaves locks unreclaimed and logs an error.
