# File Research: sources/os/linux/linux/fs/lockd/svc4proc.c

## Purpose
`svc4proc.c` implements server-side NLM version 4 RPC procedures. It adapts generated NLMv4 XDR structures to the legacy lockd server internals, performs host and file lookup, invokes shared lock/share engines, handles async callback variants, and publishes the NLMv4 `svc_version` procedure table.

## Main Responsibilities
- Defines wrapper structures whose first field is the xdrgen type and whose trailing fields hold legacy `nlm_lock`, `nlm_cookie`, or `nlm_reboot` state.
- Converts generated XDR objects (`nlm4_lock`, `netobj`, strings) into internal `nlm_lock` and `nlm_cookie` representations.
- Looks up monitored or non-monitored hosts via `nlmsvc_lookup_host()` and optional `nsm_monitor()`.
- Opens/looks up files via `nlm_lookup_file()`, validates NLMv4 64-bit offset/length ranges, initializes `struct file_lock`, and attaches lockd lock-manager operations.
- Implements synchronous procedures: NULL, TEST, LOCK, CANCEL, UNLOCK, GRANTED, GRANTED_RES, SM_NOTIFY, SHARE, UNSHARE, NM_LOCK, and FREE_ALL.
- Implements `_MSG` async forms by computing a result into an allocated `nlm_rqst` and dispatching an async reply callback.
- Defines unused procedure slots and the `nlm4svc_procedures[24]` table consumed by SUNRPC.

## Key Procedure Behavior
- `nlm4svc_proc_test()` returns whether a requested read/write lock would conflict; when denied, it fills holder details from the conflicting `nlm_lock`.
- `nlm4svc_do_lock()` is the common monitored/non-monitored lock path used by `LOCK` and `NM_LOCK`.
- `nlm4svc_proc_cancel()` rejects requests during grace period and cancels a matching blocked lock through `nlmsvc_cancel_blocked()`.
- `nlm4svc_proc_unlock()` rejects during grace period, looks up the file with `F_UNLCK`, and calls `nlmsvc_unlock()`.
- `nlm4svc_proc_granted()` and `*_granted_msg()` hand server grant callbacks to the lockd client side through `nlmclnt_grant()`.
- `nlm4svc_proc_granted_res()` converts the cookie and notifies `nlmsvc_grant_reply()`.
- `nlm4svc_proc_sm_notify()` accepts only privileged NSM callbacks, maps XDR notify fields into `nlm_reboot`, and calls `nlm_host_rebooted()`.
- `nlm4svc_proc_share()`/`unshare()` wrap share arguments as a pseudo read lock with `LOCKD_SHARE_SVID` and call `nlmsvc_share_file()` / `nlmsvc_unshare_file()`.
- `nlm4svc_proc_free_all()` frees all server-side resources for the caller host.

## Integration Points
- Uses generated NLMv4 XDR functions from `nlm4xdr_gen.h`.
- Uses common lockd engines from `svclock.c`, `svcshare.c`, and `svcsubs.c`.
- Uses status constants and internal status mapping from lockd headers.
- Uses SUNRPC async callback APIs via `nlm_async_reply()`.

## Concurrency and Lifetime Notes
- Host references returned by lookup are always released with `nlmsvc_release_host()`.
- File references returned by lookup are released with `nlm_release_file()`.
- Lockowner references set in `nlmsvc_locks_init_private()` are released after lock operations with `nlmsvc_release_lockowner()` or, in the async TEST_MSG path, with `nlmsvc_put_lockowner()` after saving the owner pointer.
- `nlm4svc_callback()` takes ownership of the supplied host reference, allocates a call, and relies on RPC release callbacks to release the call.

## Risks and Edge Cases
- `nlm4_netobj_to_cookie()` rejects cookies longer than `NLM_MAXCOOKIELEN` with `nlm_lck_denied_nolocks`.
- `nlm4svc_lookup_file()` rejects file handles larger than `NFS_MAXFHSIZE` and detects offset/length overflow, returning `nlm4_fbig`.
- The file lookup mode is `O_RDWR` for TEST paths but derived from lock type for mutating paths.
- The code deliberately supports callback procedures with host lookup inside the procedure rather than relying on `rq_client`.
