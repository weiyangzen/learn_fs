# File Research: sources/os/linux/linux-stable/fs/lockd/clntlock.c

Client-side NLM lock blocking and reclaim support.

Main entry points:
- `nlmclnt_init()` starts lockd for an NFS mount, selects NLM version 1 for NFSv2 or version 4 otherwise, looks up/binds an `nlm_host`, and stores NFS client callbacks.
- `nlmclnt_done()` releases the host and decrements lockd service usage.
- `nlmclnt_prepare_block()`, `nlmclnt_queue_block()`, `nlmclnt_dequeue_block()`, and `nlmclnt_wait()` manage blocking lock wait state.
- `nlmclnt_grant()` matches incoming GRANTED callbacks against blocked requests by lock range, synthetic owner pid, peer address, and file handle.

Recovery:
- `nlmclnt_recovery()` spawns a per-host reclaimer thread once per reboot episode.
- `reclaimer()` moves granted locks to a reclaim list, rebinds the peer, calls `nlmclnt_reclaim()` for each lock, restarts if the server reboots again, then wakes blocked waiters with grace-period status.

Synchronization:
- Global `nlm_blocked` is protected by `nlm_blocked_lock`.
- Host reclaim uses `host->h_rwsem`.
- Reclaimer holds an extra host reference and lockd service reference.
