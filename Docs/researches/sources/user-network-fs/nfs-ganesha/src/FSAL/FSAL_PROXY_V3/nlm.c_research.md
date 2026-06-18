# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/nlm.c

## Purpose
`nlm.c` implements PROXY_V3 byte-range lock operations by translating Ganesha FSAL lock requests into NLM v4 RPCs against the backend NFSv3 server's lock manager.

## Important APIs, Types, And Functions
`proxyv3_nlm_init()` caches a client machine name and process id for NLM owner fields. `proxyv3_is_valid_lockop()` rejects unsupported async/blocking locks, non-POSIX locks, missing owners, missing TEST conflict output, and missing NLM port. `proxyv3_nlm_fill_common_args()` fills cookies and `nlm4_lock` fields from the remote fh3, Ganesha state owner, lock range, machine name, and pid. `proxyv3_nlm_commonrpc()` sends the RPC and maps NLM status through `nlm4stat_to_fsalstat()`.

Operation-specific helpers are `proxyv3_nlm_test()`, `proxyv3_nlm_lock()`, `proxyv3_nlm_cancel()`, and `proxyv3_nlm_unlock()`. `proxyv3_clear_conflicting_lock()` initializes conflict output to a whole-file exclusive lock when exact holder information is not available. The exported entry point is `proxyv3_lock_op2()`.

## Control Flow
`proxyv3_lock_op2()` casts the owner, determines whether the requested lock is exclusive, pre-clears conflict output if supplied, validates the request, and dispatches by `fsal_lock_op_t`. TEST sends `NLMPROC4_TEST` and, on `NLM4_DENIED`, fills `conflicting_lock` from `nlm4_holder`. LOCK sends nonblocking `NLMPROC4_LOCK`, preserving reclaim and using `state->state_seqid` as the NLM state. UNLOCK and CANCEL send their corresponding NLM calls. All calls use `proxyv3_nlm_call()` from `rpc.c` with current `op_ctx->creds`.

## State And Persistence
The file stores only process-global NLM client identity: `nlmMachineName` and `nlmSvid`. Actual lock ownership is represented by backend lockd state keyed by caller name, pid, file handle, owner bytes, and byte range. Cookies reuse the beginning of the remote fh3 and are capped at 32 bytes for Linux lockd compatibility.

## Dependencies And Integration Points
It depends on NLM XDR types, Ganesha `nlm_util.h`, `proxyv3_fsal_methods.h`, backend NLM port discovery from export setup, and the RPC transport wrappers. It is connected to Ganesha through `PROXY_V3.handle_ops.lock_op2`.

## Risks
Blocking locks are explicitly unsupported, so any path that reaches `FSAL_OP_LOCKB` is treated as a server fault. Cookie generation from file-handle bytes is simple and can collide for handles sharing a prefix. Crash/recovery behavior is only noted as a TODO; backend lockd may try to recover with this proxy as its client while Ganesha has separate client state. `state` is assumed non-NULL for LOCK because `state->state_seqid` is used. For non-TEST lock conflicts, exact holder data is unavailable and the code reports a whole-file write conflict.

## Test Signals
Exercise LOCK, UNLOCK, TEST conflict, reclaim, NLM unavailable, grace-period, deadlock, stale file handle, read-versus-write lock compatibility, and owner byte preservation. Recovery tests should restart the proxy while locks exist on the backend. Validate Ganesha client-visible errors produced from `NLM4_DENIED`, `NLM4_BLOCKED`, and `NLM4_DENIED_GRACE_PERIOD`.
