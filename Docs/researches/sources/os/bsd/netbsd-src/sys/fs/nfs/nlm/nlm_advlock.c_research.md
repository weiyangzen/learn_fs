# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_advlock.c

This file implements the NFS client advisory byte-range lock bridge between local `VOP_ADVLOCK` operations and remote NLM RPCs. It handles `F_SETLK`, `F_UNLCK`, and `F_GETLK`, maps local process/file lock ownership to NLM wire SVIDs, performs synchronous and blocking NLM calls, copes with lockd timeouts and server grace periods, records successful remote locks in the local lock manager, and reclaims or frees locks during server reboot and vnode reclaim.

Key entry points:
- `nlm_advlock()` is the VOP-facing wrapper around `nlm_advlock_internal()`.
- `nlm_reclaim()` cancels waits for a vnode and iterates local locks to free remote locks during vnode reclaim.
- `nlm_client_recovery()` reclaims all local locks for a host after server reboot, restarting if the remote NSM state changes mid-recovery.
- `nlm_setlock()`, `nlm_clearlock()`, and `nlm_getlock()` implement remote lock, unlock, and test operations.
- `nlm_record_lock()` mirrors successful remote lock/unlock operations into the local lock manager using an NLM client sysid.
- `nlm_init_lock()` converts `struct flock` ranges, file handles, caller/owner identity, and SVID into an `nlm4_lock`.

Important behavior:
- Before lock or unlock operations, `nlm_advlock_internal()` flushes pending writes and invalidates cached data via the mount's `nm_vinvalbuf()` hook. This preserves expected cross-client file visibility around locks.
- The implementation obtains file handle, server address, NFS version, file size, and timeout from the mount's `nm_getinfo()` hook. NFSv3 mounts use NLM version 4; older mounts use NLM version 1.
- For soft mounts, retry count comes from `nm_retry`; for hard mounts, retries are effectively unbounded via `INT_MAX`.
- The current thread temporarily switches to mount credentials so NLM RPC traffic can use privileged-port credentials, then restores the original credentials and releases the temporary credential reference.
- `F_FLOCK` locks receive per-file synthetic SVIDs from an `unrhdr` allocator. The code tracks active whole-file flock ownership and stores credentials for later recovery.
- Blocking flock upgrades from shared to exclusive are approximated by first attempting a nonblocking write lock, then unlocking and retrying as blocking if denied.
- Blocking locks are registered in the NLM wait list before RPC transmission. If the server returns `nlm4_blocked`, the client waits for a granted callback but periodically retries to handle lost callbacks, broken servers, or server reboots.
- If a blocking wait is interrupted or otherwise fails, the code sends NLM CANCEL and keeps retrying cancellation across transient RPC failures.
- NLM server grace-period replies cause sleeps and exponential retry backoff up to 30 seconds in the lock path; unlock and test paths also sleep/retry on grace.
- `nlm_map_status()` maps NLM results to Unix errors: denied to `EAGAIN`, no locks to `ENOLCK`, deadlock to `EDEADLK`, read-only to `EROFS`, stale file handle to `ESTALE`, file too large to `EFBIG`, failed to `EACCES`, and unknown statuses to `EINVAL`.
- Successful non-reclaim lock operations are recorded locally and the host is registered with NSM monitoring so reboot notifications can trigger recovery.
- During recovery and reclaim, the file uses stored owner credentials where possible, falls back to the recovery thread credential when necessary, and uses `F_REMOTE` to preserve remote SVIDs or avoid local lock-manager updates for vnode teardown.

RPC version bridging:
- The core code uses NLMv4 structures internally, then helper wrappers translate to NLMv1 wire structures for older servers.
- `nlm_test_rpc()`, `nlm_lock_rpc()`, `nlm_cancel_rpc()`, and `nlm_unlock_rpc()` dispatch to `nlm4_*_4()` for version 4 or convert arguments/results for `nlm_*_1()`.
- Conversion helpers map common lock, holder, and result fields between 32-bit NLMv1 offsets/lengths and 64-bit NLMv4 representations. `nlm_init_lock()` rejects ranges that overflow NLMv1.

Concurrency and integration:
- `nlm_client_init()` initializes the SVID mutex, allocator, and hash lists at `SI_SUB_LOCK`.
- SVID records are protected by `nlm_svid_lock`; the allocation path handles races by allocating outside the list, then rechecking under lock before insertion.
- `nlm_record_lock()` may block registering locally even after the remote server granted a lock. It handles local `EDEADLK` by briefly pausing and retrying because remote grant order can differ from local lock graph timing.
- `nlm_feedback()` marks the mount with `NFSSTA_LOCKTIMEO` and emits `VQ_NOTRESPLOCK`/recovery events when lockd stops responding or recovers.

Research notes:
- This is the highest-value NLM client file in the group. It defines the semantics users see for `fcntl`/`flock` locks on NFS mounts.
- Review should focus on credential switching, vnode unlock windows, blocking wait/cancel races, SVID lifetime, local/remote lock divergence, recovery idempotence, and range conversion for negative lengths or `SEEK_END`.
