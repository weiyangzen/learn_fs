# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_callback.c

## Summary
Implements the NFSv4 client callback service and delegation lifecycle machinery. It receives server callbacks, serves CB_GETATTR/CB_RECALL/CB_NULL, registers per-server callback program numbers, manages callback state per zone, and returns, discards, reopens, or abandons delegations.

## Main Responsibilities
- Dispatches NFSv4 callback RPC procedures and compounds.
- Handles `CB_GETATTR` for delegated files, returning change and size attributes.
- Handles `CB_RECALL` by asynchronously returning delegations.
- Tracks callback ports and callback RPC program numbers used in SETCLIENTID.
- Provides `nfs4_svc()` for userland callback service setup and delegation query.
- Initializes and tears down per-zone callback globals and kstats.
- Cleans all delegations during zone shutdown/finalization.
- Performs synchronous and asynchronous `DELEGRETURN`.
- Reopens delegation-created open streams before returning recalled delegations.
- Accepts newly granted read/write delegations and records them on server delegation lists.
- Synchronizes ordinary file operations with active recall/return work.
- Maintains a recovery-time dlist of delegations that must be returned or discarded later.

## Key APIs
- Callback service: `nfs4_callback_init()`, `nfs4_callback_fini()`, `nfs4_svc()`, `nfs4_cb_args()`, `nfs4callback_destroy()`.
- Callback globals: `nfs4_get_callback_globals()`.
- Delegation return: `nfs4delegreturn()`, `nfs4delegreturn_async()`, `nfs4_do_delegreturn()`, `nfs4_resend_delegreturn()`, `nfs4delegreturn_cleanup()`.
- Delegation bulk/discard paths: `nfs4_delegreturn_all()`, `nfs4_deleg_discard()`, `nfs4delegabandon()`.
- Delegation accept/recovery sync: `nfs4_delegation_accept()`, `wait_for_recall()`, `nfs4_end_op_recall()`, `nfs4_dlistclean()`.

## Important Behavior
`cb_dispatch()` decodes callback RPC arguments, invokes `cb_null()` or `cb_compound()`, sends the reply, frees per-op response storage, and frees decoded arguments.

`cb_compound()` copies the request tag into the response, rejects unsupported callback minor versions, allocates one response slot per argument op, executes operations in order, and truncates the response array when an op returns an error. It handles `OP_CB_GETATTR`, `OP_CB_RECALL`, and illegal/default callback ops.

`cb_getattr()` maps the request RPC program to an `nfs4_server_t`, validates the server program, finds the delegated rnode by filehandle, and replies only with supported `FATTR4_CHANGE` and `FATTR4_SIZE`. For mmapped write delegations it increments the delegation change value before returning it; if the file is not dirty, it can reset the change attribute to the grant-time value. It reads size atomically to avoid locking deadlocks.

`cb_recall()` validates both delegation stateid and filehandle, then starts `nfs4delegreturn_async()` with recall/reopen flags. The async thread owns the vnode hold passed from the callback path and releases it after return processing.

`nfs4_cb_args()` associates an NFS server with an available callback program number and a previously registered transport address. Program numbers are selected from a per-zone `nfs4prog2server[]` array and reused across SETCLIENTID by first destroying the old mapping.

`nfs4_svc()` is the kernel entry point used by the mount-side helper. It supports `NFS4_DQUERY`, callback port registration, and kernel RPC transport creation through `svc_tli_kcreate()`.

## Delegation Lifecycle
`nfs4_delegation_accept()` records read/write delegations granted by OPEN. It stores stateid, permissions, space limit, grant-time change attribute, credential, and server-list membership under the required server/rnode lock ordering. It may immediately schedule a return when the server grants a recalled delegation, when policy is `IMMEDIATE`, when grant attributes are incomplete, or when an existing delegation becomes tainted.

`nfs4delegreturn_impl()` is the main return engine. It can discard without over-the-wire RPC, defer if the caller already holds start-op state, push dirty pages, take `r_deleg_recall_lock` in writer mode, optionally reopen delegation open streams, and either discard or call `nfs4_do_delegreturn()`.

`nfs4_do_delegreturn()` wraps `nfs4_start_fop()`/`nfs4_end_op()`, handles recov-only cases by creating lost request state, sends PUTFH/GETATTR/DELEGRETURN via `nfs4delegreturn_otw()`, updates the attribute cache from GETATTR on success, and starts recovery when retryable or state-related errors require it.

`deleg_reopen()` finds open streams that were created under the delegation and reopens them using `CLAIM_DELEGATE_CUR` or `CLAIM_NULL` depending on whether the delegation is being discarded. It handles EAGAIN retry, errors that already started recovery, and recovery-start decisions for other protocol failures.

`nfs4delegreturn_thread()` services async recall/abandon work. It holds `r_rwlock` in reader mode to stop non-mmap mutation during recall, flushes or invalidates pages for truncate/write/failed-recovery cases, removes recursive `NFS4_DR_DID_OP`, invokes `nfs4delegreturn_impl()`, and drops the vnode reference.

## State and Synchronization
Per-zone `nfs4_callback_globals` owns the callback program-to-server array, callback port list, delegation cleanup dlist, locks, and kstats. Zone shutdown cleans the dlist and discards delegations; finalization repeats discard, removes zone servers from the global list, frees callback ports, destroys lists/locks, and frees globals.

Delegation list membership is anchored in `nfs4_server_t.s_deleg_list` and protected by `s_lock`; per-rnode delegation fields use `r_statev4_lock`, while page/dirty flags use `r_statelock`. The code documents and follows lock ordering around `s_lock`, `r_statev4_lock`, `r_deleg_recall_lock`, `mi_recovlock`, and `r_rwlock`.

The dlist path marks `r_deleg_return_pending`, holds the vnode, stores return flags in `struct nfs4_dnode`, and later drains the list through `nfs4delegreturn_impl()`.

## Dependencies
This file depends on illumos kernel RPC service plumbing, zone-specific data, kstats, NFSv4 client recovery, rnode/open-stream state, page flushing/invalidation, XDR-generated callback structures, and server-list reference management.

## Risks
The callback-to-server mapping trusts the RPC program number after range checks; stale or confused program mappings generally fail with `BADHANDLE`/`BAD_STATEID`, but all delegation work depends on correct registration and cleanup.

Delegation return spans RPC, recovery, vnode lifetime, page flushing, open-stream reopening, and multiple lock domains. The comments repeatedly note deadlock risks around `nfs4_start_fop()`, `VOP_PUTPAGE()`, and recall locks.

`nfs4_callback_fini()` is empty even though `nfs4_callback_init()` allocates the service callout table. This may rely on module lifetime semantics, but it is a visible lifetime asymmetry.

The async paths depend on callers taking `VN_HOLD()` before thread creation. Any new caller of `nfs4delegreturn_async()` must preserve that contract.
