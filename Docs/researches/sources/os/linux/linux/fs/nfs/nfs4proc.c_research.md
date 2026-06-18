# File Research: sources/os/linux/linux/fs/nfs/nfs4proc.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9520, source bytes 262135, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nfs_nfs4proc_c_1_1_9520_f6c8012c3536_research.md`
- chunk 2: lines 9521-10754, source bytes 32986, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nfs_nfs4proc_c_2_9521_10754_0ef2d18db04f_research.md`

## Chunk Research

### Chunk 1: lines 1-9520

# Chunk Research: sources/os/linux/linux/fs/nfs/nfs4proc.c lines 1-9520

## Scope

This chunk covers the beginning through the NFSv4.1 `RECLAIM_COMPLETE` path in `fs/nfs/nfs4proc.c`. It includes most core client-side NFSv4 procedure wrappers: error/recovery handling, sequence-slot management, OPEN/CLOSE stateid handling, metadata operations, directory operations, read/write/commit setup, ACL/security-label xattrs, delegation return, locking, referrals/migration helpers, `SETCLIENTID`, `EXCHANGE_ID`, session creation/destruction, lease renewal, and reclaim-complete. The next chunk begins in the pNFS layout operation area immediately after this range.

## Primary APIs and Entry Points

- Error and retry APIs: `nfs4_map_errors`, `nfs4_handle_exception`, `nfs4_async_handle_exception`, and `nfs4_async_handle_error` normalize negative NFSv4 protocol statuses into Linux errno values or schedule recovery/retry/delay behavior.
- Session/sequence APIs: `nfs4_init_sequence`, `nfs4_setup_sequence`, `nfs41_sequence_done`, `nfs4_sequence_done`, `nfs4_call_sync`, and `nfs4_call_sync_sequence` attach NFSv4.1 sequence slots to RPC tasks and drive synchronous compounds through the minor-version operation table.
- OPEN/CLOSE APIs: `nfs4_do_open`, `nfs4_atomic_open`, `nfs4_close_context`, `nfs4_do_close`, `nfs4_open_reclaim`, `nfs4_open_expired`, and `nfs4_open_delegation_recall` allocate `nfs4_opendata`, run `OPEN`/`OPEN_CONFIRM`, update stateids, and recover opens after reboot, expiration, or delegation recall.
- Metadata and namespace APIs: `nfs4_server_capabilities`, `nfs4_proc_get_rootfh`, `nfs4_proc_getattr`, `nfs4_proc_setattr`, lookup/lookupp/access/readlink/create/remove/rmdir/link/symlink/mkdir/readdir/mknod/statfs/fsinfo/pathconf wrappers expose NFSv4 compounds to the VFS-facing NFS client ops.
- I/O setup APIs: `nfs4_proc_read_setup`, `nfs4_proc_pgio_rpc_prepare`, `nfs4_read_done`, `nfs4_proc_write_setup`, `nfs4_write_done`, `nfs4_proc_commit_setup`, and `nfs4_proc_commit` prepare stateids, sequence args, bitmasks, callbacks, and state-protection credentials for page I/O and COMMIT.
- ACL/xattr APIs: `nfs4_proc_get_acl`, `nfs4_proc_set_acl`, NFSv4 ACL xattr handlers, optional security-label handlers, and NFSv4.2 user-xattr helpers bridge Linux xattr APIs to NFSv4 `GETACL`, `SETACL`, and NFSv4.2 xattr operations.
- Client/session lifecycle APIs: `nfs4_proc_setclientid`, `nfs4_proc_setclientid_confirm`, `nfs4_proc_exchange_id`, `nfs4_proc_create_session`, `nfs4_proc_destroy_session`, `nfs4_destroy_clientid`, `nfs4_proc_get_lease_time`, `nfs41_proc_async_sequence`, `nfs4_proc_sequence`, and `nfs41_proc_reclaim_complete`.
- Locking and lease APIs: `nfs4_proc_lock`, `nfs4_proc_setlease`, `nfs4_lock_reclaim`, `nfs4_lock_expired`, and `nfs4_lock_delegation_recall` manage POSIX/flock-style locks, lock stateids, lock retries, delegation-cached locks, and callback wakeups.

## Control Flow

- Most public wrappers follow a two-layer pattern: an internal `_nfs4_*` routine builds a compound argument/result pair and calls `nfs4_call_sync` or launches an async `rpc_task`; an outer `nfs4_*` routine loops through `nfs4_handle_exception` until `exception.retry` is false.
- `nfs4_do_handle_exception` is the central control point for protocol errors. It schedules stateid recovery, lease recovery, session recovery, migration recovery, lease-moved recovery, or bounded delay depending on the status. It treats session sequence errors as already handled by `nfs41_sequence_process`.
- NFSv4.1 sequencing is integrated into RPC callbacks. Prepare callbacks call `nfs4_setup_sequence`; done callbacks call `nfs41_sequence_done` or `nfs4_sequence_done`; slots are released only after the sequence state machine records success, retries, sequence misordering, or session reset.
- `nfs41_sequence_process` handles `SEQUENCE`-level outcomes, including slot acking, target slot updates, `NFS4ERR_DELAY`, false retry, bad slot, sequence misordering, dead/bad sessions, and draining the slot table before scheduling session recovery.
- OPEN flow starts with state-owner acquisition and lease recovery, optionally uses cached open/delegation state, sends `OPEN`, optionally sends `OPEN_CONFIRM`, maps returned file handles/attrs to an inode/state, processes delegations, performs access checks, and attaches the open context.
- CLOSE flow allocates `nfs4_closedata`, selects `CLOSE` versus `OPEN_DOWNGRADE` based on remaining per-mode open counts, optionally folds pNFS return-on-close layoutreturn args into the compound, requests close-to-open consistency attributes when no delegation covers reads, then updates or clears the open stateid.
- Namespace operations update local cache state after successful server change-info responses. `nfs4_update_changeattr` invalidates directory data, nlink, access, ACL, size, xattr, and other inode fields depending on the operation and whether attributes are delegated.
- Read/write paths choose a current read/write stateid during RPC prepare. Done callbacks restart the task if the server reports an expired/old/openmode stateid and the locally selected current stateid has changed.
- Client setup differs by minor version: NFSv4.0 uses `SETCLIENTID`/`SETCLIENTID_CONFIRM`; NFSv4.1+ uses `EXCHANGE_ID`, state-protection negotiation, `CREATE_SESSION`, slot-table setup, connection binding, trunk discovery, and `SEQUENCE` lease renewal.

## State and Data Structures

- `nfs_client` state touched here includes clientid, exchange flags, session pointer, slot table, sequence id, state-protection flags, owner id string, acceptor string, last renewal timestamp, session-established bit, migration/recovery flags, server owner/scope/implementation IDs, and lock waitqueue.
- `nfs_server` state is updated with server capability flags, supported attribute bitmasks, security-label/no-label bitmasks, cache-consistency bitmasks, exclusive-create bitmasks, ACL support mask, file-handle expiry type, filesystem id, pNFS block size, and pNFS layout driver.
- `nfs4_state` tracks open and delegation stateids, open mode counters (`n_rdonly`, `n_wronly`, `n_rdwr`), open/delegated/lock flags, lock-state list, waitqueue, seqlock, and owner reference. This chunk carefully serializes stateid changes with owner locks, seqlocks, state locks, waitqueues, and RCU.
- `nfs4_opendata`, `nfs4_closedata`, `nfs4_lockdata`, `nfs4_unlockdata`, `nfs4_delegreturndata`, and `nfs4_reclaim_complete_data` are per-RPC callback payloads. They hold args, results, sequence state, inode/state references, credentials, timestamps, retrans counters, and pNFS layoutreturn sub-arguments where needed.
- Attribute bitmasks are not static request constants in practice. Helpers trim delegated attributes from `GETATTR` requests and add invalidated attributes back into close/write/delegreturn cache-consistency requests.
- ACL state is cached in `NFS_I(inode)->nfs4_acl`, with small ACL bodies copied into a kmalloc buffer and large/length-only ACLs represented as uncached length metadata.

## Dependencies and Integration Points

- SUNRPC dependencies: `rpc_run_task`, `rpc_call_sync`, `rpc_wait_for_completion_task`, `rpc_restart_call_prepare`, `rpc_sleep_on`, `rpc_delay`, transport release, xprt iteration, trunk add/remove, auth flavor and credential APIs.
- NFS core dependencies: inode/fh/fattr helpers, open context helpers, access cache, attr invalidation, dentry verifier/splice behavior, revalidation, sillyrename/delegation-on-close hooks, state owner/seqid allocation, and state manager scheduling.
- NFSv4 support modules: `nfs4_fs.h`, `delegation.h`, `callback.h`, `nfs4session.h`, `nfs40.h`, `nfs42.h`, `pnfs.h`, `nfs4idmap.h`, `sysfs.h`, and `nfs4trace.h`.
- pNFS integration appears throughout but is not fully defined in this chunk: open layoutget preparation/parsing, return-on-close, layoutreturn waiting, write/commit data-server client handling, layout driver selection from `FSINFO`, and pNFS cleanup state protection.
- LSM/security dependencies include `security_dentry_init_security`, `security_release_secctx`, `security_ismaclabel`, optional `CONFIG_NFS_V4_SECURITY_LABEL`, and security-label fattr handling.
- VFS/locking dependencies include `struct inode`, `dentry`, `file_lock`, generic file leases, Linux lock manager APIs, inode semaphores, dcache alias pruning, and xattr handler callbacks.

## Risks and Subtle Behaviors

- Stateid ordering is race-prone. The code relies on server stateid seqids, local seqlocks, owner locks, and waitqueues to process concurrent OPEN/CLOSE/OPEN_DOWNGRADE/LOCK/LOCKU updates in server order.
- Error handling can intentionally hide protocol details from userspace. Unhandled NFSv4 protocol errors are mapped to generic errno values, often `-EIO`, after recovery attempts.
- Async cancellation paths must clean up successful-but-cancelled state by issuing close/unlock operations. Several release callbacks conditionally close state or unlock a lock if the RPC completed after local cancellation.
- Delegations alter both correctness and performance. Cached opens/locks avoid RPCs, but incompatible delegation returns, revoked delegation cleanup, and delegated timestamp return paths must be synchronized with state recovery and pNFS layout return.
- Attribute cache correctness depends on precise bitmask adjustment. Requesting too little risks stale metadata; requesting unsupported or delegated attributes can cause server errors or unnecessary RPC payload.
- Security fallback paths are deliberate. Root lookup and SECINFO retry across auth flavors, and the SP4_MACH_CRED fallback from `SP4_MACH_CRED` to `SP4_NONE`, are compatibility paths for real servers.
- NFSv4.1 session recovery is coupled to sequence-slot errors. Bad session/slot/misordered sequence handling can drain slot tables, trigger manager recovery, and cause task restarts with or without delay.
- Some loops use sleep/retry on server `DELAY`, `GRACE`, or busy states. Soft-error mounts are bounded by `nfs_delay_retrans`; other recovery paths can continue until the state manager resolves the condition or a fatal signal occurs.
- The delegation recall lock helper contains a visible typo-like comparison to `-NFSERR_GRACE` in a loop condition after checking `-NFS4ERR_GRACE`; this should be reviewed against available constants in adjacent headers before treating it as a bug.

## Cross-Chunk References

- The range ends just before the pNFS layoutget/layoutreturn/layoutcommit implementations. This chunk calls into pNFS helpers and starts the `nfs4_layoutget_prepare` / `nfs4_layoutget_done` area after line 9520, so later chunk(s) must complete the layout operation story.
- Minor-version operation tables and final `nfs_v4_clientops`, inode ops, xattr handler arrays, and clone-server wiring are outside this chunk but are referenced by many functions through `cl_mvops`, `nfs4_procedures`, and exported wrapper functions.
- NFSv4.1 `test_stateid` and `free_stateid` are forward-declared and called for expired/revoked state cleanup in this chunk; their implementations appear after this range.
- NFSv4.2 xattr and read-plus support is partially represented here through guards and calls to `nfs42_proc_*`; the procedure implementations live in NFSv4.2-specific files or later code.
- Folder-level and final per-file synthesis should merge this chunk with the trailing part of `nfs4proc.c` to cover pNFS layouts, stateid test/free, minor-version ops tables, client ops registration, and xattr handler arrays.

### Chunk 2: lines 9521-10754

# Chunk Research: sources/os/linux/linux/fs/nfs/nfs4proc.c lines 9521-10754

## Scope

This chunk covers the tail of NFSv4.1 reclaim-complete RPC handling, pNFS `LAYOUTGET` / `LAYOUTRETURN` / `GETDEVICEINFO` / `LAYOUTCOMMIT`, NFSv4.1 `SECINFO_NO_NAME`, stateid test/free helpers, minor-version operation tables for NFSv4.1/v4.2, VFS inode operation tables, NFSv4 client RPC operation registration, and NFSv4 xattr handler registration.

Primary lines covered: `sources/os/linux/linux/fs/nfs/nfs4proc.c:9521-10754`.

The range begins inside `nfs4_reclaim_complete_done()` at the restart/return path; adjacent preceding lines define the callback's sequence completion and reclaim-complete error handler.

## APIs and Entry Points

- `nfs41_proc_reclaim_complete()` issues a global NFSv4.1 `RECLAIM_COMPLETE` using `clp->cl_rpcclient`, a privileged sequence, and `nfs4_reclaim_complete_call_ops`.
- `nfs4_proc_layoutget()` sends asynchronous `LAYOUTGET`, waits for completion, converts pNFS layout errors into Linux errno/retry signals, and returns either a `struct pnfs_layout_segment *` or `ERR_PTR(status)`.
- `max_response_pages()` computes the page-array length required for the session's maximum response size.
- `nfs4_proc_layoutreturn()` sends `LAYOUTRETURN`, optionally asynchronously, protects cleanup with machine credentials when required, and lets release handling free or retry local layout segments.
- `nfs4_proc_getdeviceinfo()` wraps `_nfs4_proc_getdeviceinfo()` with `nfs4_handle_exception()` retry handling and is exported with `EXPORT_SYMBOL_GPL`.
- `nfs4_proc_layoutcommit()` sends `LAYOUTCOMMIT`, either synchronously or asynchronously, and cleans pNFS layoutcommit state on task release.
- `_nfs41_proc_secinfo_no_name()`, `nfs41_proc_secinfo_no_name()`, and `nfs41_find_root_sec()` implement root security-flavor discovery through `SECINFO_NO_NAME`, with fallback to older root security probing.
- `_nfs41_test_stateid()` and `nfs41_test_stateid()` perform `TEST_STATEID` and handle delay/session retry classes.
- `nfs41_free_stateid()` sends asynchronous `FREE_STATEID`; `nfs41_free_lock_state()` uses it before freeing local lock state.
- `nfs41_match_stateid()` implements NFSv4.1 stateid matching, treating a zero sequence id as a wildcard; exported `nfs4_match_stateid()` delegates to generic `nfs4_stateid_match()`.
- `nfs_v4_minor_ops[]` registers minor-version operation tables for NFSv4.1 and, when compiled, NFSv4.2.
- `nfs4_listxattr()` merges generic, LSM/security, and NFSv4.2 user xattr names.
- `nfs4_enable_swap()` and `nfs4_disable_swap()` control NFSv4 state-manager liveness for swap usage.
- `nfs4_clone_server()` clones a server, applies session size limits, and allocates the NFSv4 delegation hash.
- `nfs_v4_clientops` publishes NFSv4 operations to the generic NFS client/VFS layer.
- `nfs4_xattr_handlers[]` publishes NFSv4 ACL, DACL, SACL, security-label, and NFSv4.2 user-xattr handlers.

## Control Flow

### Reclaim complete

The visible part of `nfs4_reclaim_complete_done()` restarts the RPC call after `nfs41_reclaim_complete_handle_errors()` returns `-EAGAIN`. `nfs41_proc_reclaim_complete()` allocates callback data, sets `one_fs = 0` for global completion, initializes an NFSv4 sequence with privileged/machine-credential semantics, then executes a synchronous custom RPC task. The callback release path frees the allocated data.

### pNFS `LAYOUTGET`

`nfs4_proc_layoutget()` initializes a sequence, runs an async moveable RPC task with `RPC_TASK_CRED_NOREF`, then waits for completion. Successful replies with a non-empty layout are passed to `pnfs_layout_process()`. Empty layout replies are treated as retryable `-EAGAIN` with updated delay.

`nfs4_layoutget_handle_exception()` frees the sequence slot before exception processing and maps important pNFS protocol statuses:

- `NFS4ERR_LAYOUTUNAVAILABLE` becomes `-ENODATA`, telling higher layers to retry without pNFS.
- `NFS4ERR_BADLAYOUT` becomes `-EOVERFLOW`.
- `NFS4ERR_LAYOUTTRYLATER` becomes `-EBUSY` unless `minlength == 0`, where it becomes `-EOVERFLOW`.
- recall/return conflicts become `-ERECALLCONFLICT`.
- revoked/expired/bad stateids either attach the open state/stateid to the exception for recovery or mark the layout stateid invalid, commit dirty data, free affected layout segments, and retry.

All other statuses delegate to `nfs4_handle_exception()` and translate its retry decision into `-EAGAIN` where appropriate.

### pNFS `LAYOUTRETURN`

`nfs4_proc_layoutreturn()` first applies NFSv4 state protection for pNFS cleanup. It takes an active inode reference for async operation; if that fails for async return, it releases the return object and returns `-EAGAIN`. If no inode reference is held, the operation is forced privileged. The call uses `nfs4_layoutreturn_call_ops`.

`nfs4_layoutreturn_prepare()` sets up the sequence and exits the RPC early if the layout is already invalid. `nfs4_layoutreturn_done()` handles transport failures separately from NFS status: several fatal/interrupted local RPC errors are treated as successful local cleanup, transient network errors may request retry, session errors schedule session recovery, `NFS4ERR_DELAY` may restart the call, and `NFS4ERR_OLD_STATEID` may refresh the stateid before restart.

`nfs4_layoutreturn_release()` is where local layout segment ownership is resolved. Success, or lack of an inode reference, frees returned layout segments; retryable failure queues them with `pnfs_layoutreturn_retry_later()`. It then frees sequence slots, layout-driver private data, layout header, inode/credential references, and the return allocation.

### Device info and layout commit

`_nfs4_proc_getdeviceinfo()` sends `GETDEVICEINFO` with change/delete notification requests. Unsupported notification bits are logged, and incomplete notification support marks the device as `nocache`, preventing persistent device-info caching. The public wrapper retries through the normal NFSv4 exception handler.

`nfs4_proc_layoutcommit()` creates a moveable RPC task, optionally async. The async path must hold an active inode reference; otherwise it releases the layoutcommit data and returns `-EAGAIN`. The done callback ignores layout-recall/no-layout/grace classes by clearing status, while other errors pass through `nfs4_async_handle_error()` and may restart. Release always calls `pnfs_cleanup_layoutcommit()`, forces weak-cache-consistency inode update from returned attributes, drops refs, and frees the data.

### Root security discovery

`nfs41_proc_secinfo_no_name()` first attempts `SECINFO_NO_NAME` over integrity-protected state-management RPC credentials when available. If integrity protection cannot be used, or deployed servers return `NFS4ERR_WRONGSEC` despite the spec, it retries over the filesystem RPC client/user credential path. Normal exception handling is used for other errors.

`nfs41_find_root_sec()` allocates one page for the returned flavor list, calls `SECINFO_NO_NAME`, falls back to `nfs4_find_root_sec()` on `WRONGSEC`/`ENOTSUPP`, then iterates returned `RPC_AUTH_NULL`, `RPC_AUTH_UNIX`, and `RPC_AUTH_GSS` flavors. Each candidate is converted to a pseudoflavor, checked against mount auth info, and tested with `nfs4_lookup_root_sec()`. If no candidate succeeds, it returns `-EPERM`; visible `-EACCES` is normalized to `-EPERM`.

### Stateid testing and freeing

`nfs41_test_stateid()` wraps `_nfs41_test_stateid()` in a loop that retries only delay, uncached-reply, and session-slot/session-dead classes. `_nfs41_test_stateid()` uses `nfs4_state_protect()` with `NFS_SP4_MACH_CRED_STATEID`, sends `TEST_STATEID`, and returns either the transport/compound status or the negated per-stateid result.

`nfs41_free_stateid()` increments the client reference count for async lifetime, protects the call with stateid machine credentials, copies the stateid into heap callback data, initializes a privileged sequence if requested, and runs an async moveable task. On success scheduling, it marks the caller's stateid type as `NFS4_FREED_STATEID_TYPE`. The release callback drops the client reference and frees the task data.

### Registration tables and VFS glue

The NFSv4.1 minor ops table selects NFSv4.1 capabilities, session/sequence ops, state recovery ops, migration recovery ops, root security discovery, stateid matching, lock-state freeing, and no seqid allocation. The NFSv4.2 table extends the capability mask with allocate/copy/clone/seek/layoutstats/read-plus/offload features while reusing most NFSv4.1 callbacks.

`nfs_v4_clientops` binds NFSv4 procedures from earlier in the file to generic NFS operations for mounting, lookup, attribute changes, directory ops, read/write/commit, locking, delegation handling, client/server lifecycle, trunking, and swap integration. Inode operation tables wire NFSv4 directory and file VFS operations, including `nfs4_listxattr()`.

The xattr handler array exposes NFSv4 ACL/DACL/SACL handlers unconditionally, security-label handling under `CONFIG_NFS_V4_SECURITY_LABEL`, and NFSv4.2 user xattrs under `CONFIG_NFS_V4_2`.

## State and Synchronization

- NFSv4 sessions are managed through `nfs4_init_sequence()`, `nfs4_setup_sequence()`, `nfs41_sequence_process()`, `nfs41_sequence_done()`, and explicit `nfs4_sequence_free_slot()` calls on retry/release paths.
- pNFS layout state is coordinated through `struct pnfs_layout_hdr`, layout stateids, layout segment lists, layout-driver private cleanup, and flags such as `NFS_LAYOUT_INVALID_STID`.
- `nfs4_layoutget_handle_exception()` takes `inode->i_lock` while comparing and invalidating layout stateids, then performs commit/free work after dropping the lock.
- Async pNFS operations keep inode/client/credential/layout references alive until RPC release callbacks run.
- `nfs4_state_protect()` can switch RPC clients/credentials for protected pNFS cleanup and stateid operations.
- `nfs41_free_stateid()` relies on `clp->cl_count` to keep `struct nfs_client` alive until `nfs41_free_stateid_release()`.
- `nfs4_enable_swap()` schedules the state manager; `nfs4_disable_swap()` mutates `clp->cl_state` bits and wakes waiters so the manager can re-evaluate exit conditions.
- `nfs4_clone_server()` owns the cloned server after `nfs_clone_server()` and frees it if delegation-hash allocation fails.

## Dependencies

This chunk depends heavily on Linux NFS client infrastructure:

- SunRPC task APIs: `struct rpc_task`, `struct rpc_message`, `struct rpc_task_setup`, `rpc_run_task()`, `rpc_wait_for_completion_task()`, `rpc_put_task()`, `rpc_restart_call_prepare()`, `rpc_exit()`, task flags, and `rpc_call_ops`.
- NFSv4 RPC procedure table entries such as `NFSPROC4_CLNT_RECLAIM_COMPLETE`, `LAYOUTGET`, `LAYOUTRETURN`, `GETDEVICEINFO`, `LAYOUTCOMMIT`, `SECINFO_NO_NAME`, `TEST_STATEID`, and `FREE_STATEID`.
- NFSv4 sequence/session and exception helpers: `nfs4_init_sequence()`, `nfs4_call_sync_custom()`, `nfs4_call_sync()`, `nfs4_call_sync_sequence()`, `nfs4_handle_exception()`, `nfs4_do_handle_exception()`, `nfs4_async_handle_error()`, `nfs4_schedule_session_recovery()`, and `nfs4_update_delay()`.
- pNFS helpers: `pnfs_layout_process()`, `pnfs_layoutget_free()`, `pnfs_layout_is_valid()`, `pnfs_layoutreturn_free_lsegs()`, `pnfs_layoutreturn_retry_later()`, `pnfs_mark_layout_stateid_invalid()`, `pnfs_free_lseg_list()`, `pnfs_cleanup_layoutcommit()`, and `pnfs_put_layout_hdr()`.
- State and credential helpers: `nfs4_state_protect()`, `nfs4_stateid_copy()`, `nfs4_stateid_match_other()`, `nfs4_stateid_match()`, `nfs4_get_clid_cred()`, `put_cred()`, `nfs_igrab_and_active()`, and `nfs_iput_and_deactive()`.
- VFS/security APIs: `generic_listxattr()`, `security_inode_listsecurity()`, `d_inode()`, `struct inode_operations`, and xattr handler registration.
- Mount/auth helpers: `rpcauth_get_pseudoflavor()`, `nfs_auth_info_match()`, `nfs4_lookup_root_sec()`, and `nfs4_find_root_sec()`.

## Risks and Edge Cases

- The range starts mid-callback; reclaim-complete semantics depend on preceding error handling that wakes reclaim waiters and decides when to restart.
- `nfs41_proc_reclaim_complete()` allocates with `GFP_NOFS`; allocation failure returns `-ENOMEM` before sending the protocol completion, which can prolong recovery.
- `nfs4_layoutget_handle_exception()` must free the sequence slot before exception recovery. Missing this on new retry paths would leak session slots.
- Layout stateid recovery distinguishes open-stateid failures from layout-stateid failures by comparing `lgp->args.stateid` with `lo->plh_stateid` under `inode->i_lock`; wrong classification could either trigger unnecessary open recovery or leave a bad layout stateid active.
- `LAYOUTGET` with a zero-length returned layout is treated as retryable, so repeated empty replies rely on exception timeout/backoff to avoid tight loops.
- `LAYOUTRETURN` deliberately treats several local RPC failures as successful local cleanup to avoid leaking layout segments when communication is no longer useful. This can make the metadata server unaware of a return, relying on later recovery/lease behavior.
- In `nfs4_proc_layoutreturn()`, a failed `rpc_run_task()` returns without running the normal release callback. Correct ownership depends on the caller/RPC setup contract for the `lrp` allocation on task creation failure.
- `nfs41_free_stateid()` increments `clp->cl_count` before allocating callback data, but if `kmalloc_obj(*data)` fails it returns `-ENOMEM` without dropping that reference in the visible code. The same leak risk exists if `rpc_run_task()` returns an error after data allocation.
- `nfs41_free_lock_state()` ignores the return status of asynchronous `FREE_STATEID` and frees local lock state regardless.
- `nfs41_match_stateid()` treats either zero seqid as a match wildcard after matching type and opaque bytes, which is required by NFSv4.1 stateid semantics but is a subtle difference from strict equality.
- `nfs4_listxattr()` increments `list`/`left` only after successful component list calls; final `-ERANGE` is based on aggregate size and may be reported after component functions have already filled partial output.
- `nfs4_clone_server()` must keep session size limiting and delegation-hash allocation paired with cloned-server lifetime; failure unwinds with `nfs_free_server()`.

## Cross-Chunk References

- The immediately preceding chunk defines the beginning of reclaim-complete handling, including `nfs4_reclaim_complete_prepare()`, `nfs41_reclaim_complete_handle_errors()`, and the first half of `nfs4_reclaim_complete_done()`.
- Earlier `nfs4proc.c` sections define most callbacks registered in `nfs_v4_clientops`, including lookup, create/remove/rename, read/write/commit, locking, delegation, mount, client initialization, and trunking procedures.
- Earlier NFSv4.0 minor-version code defines `nfs_v4_0_minor_ops`, referenced by `nfs_v4_minor_ops[]` when `CONFIG_NFS_V4_0` is enabled.
- Earlier NFSv4.1 session code defines `nfs41_call_sync_ops`, `nfs41_sequence_process()`, `nfs41_sequence_done()`, and `nfs41_sequence_free_slot()`, installed through `nfs41_sequence_slot_ops`.
- Earlier state recovery functions (`nfs4_open_reclaim()`, `nfs4_lock_reclaim()`, `nfs41_open_expired()`, `nfs41_lock_expired()`, `nfs41_init_clientid()`, `nfs41_discover_server_trunking()`) are assembled into reboot/no-grace recovery tables here.
- pNFS code outside this file consumes `nfs4_proc_layoutget()`, `nfs4_proc_layoutreturn()`, `nfs4_proc_getdeviceinfo()`, and `nfs4_proc_layoutcommit()` as the metadata-server RPC backend for layout acquisition, return, device discovery, and commit.
- NFSv4 ACL, security-label, and user-xattr helpers referenced in the handler tables are defined elsewhere in the NFS client xattr/ACL code and become VFS-visible through this chunk's registration arrays.

## Research Notes

This chunk is the final integration layer for NFSv4.1/v4.2 client behavior in `nfs4proc.c`: it wires pNFS protocol operations into SunRPC tasks, converts NFS protocol statuses into retry/recovery/local fallback decisions, and publishes minor-version, VFS, RPC, and xattr operation tables. The highest-risk areas are asynchronous lifetime ownership, sequence-slot cleanup on retry paths, and pNFS error classification because those decide whether the client retries, falls back to in-band I/O, frees local layout state, or schedules broader state/session recovery.
