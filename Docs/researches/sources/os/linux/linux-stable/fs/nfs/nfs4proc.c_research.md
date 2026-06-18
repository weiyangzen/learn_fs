# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4proc.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9526, source bytes 262136, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nfs_nfs4proc_c_1_1_9526_916105ce4105_research.md`
- chunk 2: lines 9527-10750, source bytes 32788, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nfs_nfs4proc_c_2_9527_10750_174064f9904c_research.md`

## Chunk Research

### Chunk 1: lines 1-9526

# Chunk Research: sources/os/linux/linux-stable/fs/nfs/nfs4proc.c lines 1-9526

## Scope

This chunk covers the beginning of the Linux stable NFSv4 client procedure file through the start of `nfs4_free_reclaim_complete_data`. It contains the bulk of client-side NFSv4 procedure machinery: attribute bitmaps, error/recovery handling, NFSv4.1 sequence-slot handling, OPEN/CLOSE stateid management, metadata and namespace operations, page I/O setup, ACL/security-label xattrs, SETCLIENTID/EXCHANGE_ID/session setup, delegation return, locking, migration/referral helpers, lease renewal, and the beginning of `RECLAIM_COMPLETE`.

## Primary APIs and Entry Points

- Error/recovery: `nfs4_map_errors`, `nfs4_handle_exception`, `nfs4_async_handle_exception`, and `nfs4_async_handle_error` translate protocol errors, schedule state/session/lease/migration recovery, delay retryable operations, and preserve async retry state.
- Sequence/session wrappers: `nfs4_init_sequence`, `nfs4_setup_sequence`, `nfs41_sequence_done`, `nfs4_sequence_done`, `nfs4_call_sync_sequence`, `nfs4_call_sync`, and `nfs4_do_call_sync` attach SEQUENCE state to RPC tasks and run compounds through minor-version-specific callbacks.
- OPEN/CLOSE and stateid APIs: `nfs4_do_open`, `nfs4_atomic_open`, `nfs4_close_context`, `nfs4_do_close`, `nfs4_open_reclaim`, `nfs4_open_expired`, `nfs41_open_expired`, `nfs4_open_delegation_recall`, and `update_open_stateid` manage open owners, seqids, open/delegation stateids, cached opens, recoveries, and open-downgrade/close.
- VFS-facing metadata/namespace operations: `nfs4_server_capabilities`, `nfs4_proc_get_rootfh`, `nfs4_proc_getattr`, `nfs4_proc_setattr`, lookup/lookupp/access/readlink/create/remove/rmdir/link/symlink/mkdir/readdir/mknod/statfs/fsinfo/pathconf wrappers expose NFSv4 compounds to higher NFS/VFS layers.
- I/O setup/completion: `nfs4_proc_read_setup`, `nfs4_proc_pgio_rpc_prepare`, `nfs4_read_done`, `nfs4_proc_write_setup`, `nfs4_write_done`, `nfs4_proc_commit_setup`, and `nfs4_proc_commit` select current stateids, handle READ_PLUS fallback, request cache-consistency attributes, and restart RPCs on stale stateids.
- ACL/security/xattr APIs: `nfs4_proc_get_acl`, `nfs4_proc_set_acl`, NFSv4 ACL xattr handlers, optional security-label handlers, and NFSv4.2 user-xattr handlers bridge Linux xattr calls to NFSv4 ACL/security-label and NFSv4.2 xattr RPCs.
- Client/session lifecycle: `nfs4_proc_setclientid`, `nfs4_proc_setclientid_confirm`, `nfs4_proc_exchange_id`, `nfs4_test_session_trunk`, `nfs4_destroy_clientid`, `nfs4_proc_get_lease_time`, `nfs4_proc_create_session`, `nfs4_proc_destroy_session`, `nfs41_proc_async_sequence`, and `nfs4_proc_sequence`.
- Locking/leases: `nfs4_proc_lock`, `nfs4_proc_setlease`, `nfs4_lock_reclaim`, `nfs4_lock_expired`, `nfs41_lock_expired`, and `nfs4_lock_delegation_recall` implement GETLK/SETLK/UNLCK, lock stateid recovery, delegated lock caching, callback wakeups, and local file leases backed by delegations.

## Control Flow

- The file uses a consistent two-layer operation pattern: an internal `_nfs4_*` helper builds protocol args/results and calls `nfs4_call_sync` or starts an async `rpc_task`; the public wrapper loops through `nfs4_handle_exception` while `exception.retry` remains set.
- `nfs4_do_handle_exception` is the central error switch. It converts stateid, lease, session, migration, delay, server-grace, idmapping, and moved errors into recovery scheduling, retry, delay, or final Linux errno mapping.
- NFSv4.1 `SEQUENCE` processing is task-callback driven. Prepare callbacks allocate/attach slots with `nfs4_setup_sequence`; done callbacks call `nfs41_sequence_done`/`nfs4_sequence_done`; slot release increments slot sequence numbers, wakes waiters, and may notify the server of lower highest-used slot IDs.
- `nfs41_sequence_process` handles success, RPC-level uncertainty, `DELAY`, retry/false-retry, bad slots, sequence misordering, bad/dead sessions, and connection-not-bound errors. Some paths restart immediately; others delay or drain the session slot table before scheduling recovery.
- OPEN flow acquires a state owner, performs client lease recovery, returns incompatible delegations, builds `nfs4_opendata`, optionally reuses cached open/delegation state, sends `OPEN`, optionally sends `OPEN_CONFIRM`, maps attrs/fh to inode/state, processes returned delegations, validates access, parses pNFS open layoutget results, and attaches the open context.
- CLOSE flow computes whether it can use `OPEN_DOWNGRADE` or must use `CLOSE`, synchronizes the outgoing open stateid, waits for return-on-close layoutreturn if needed, optionally requests close-to-open consistency attrs, and clears or updates open-state flags when the RPC completes.
- Metadata-changing operations update local cache state from NFSv4 change-info. Directory operations invalidate lookup/data caches; link count changes are adjusted locally for mkdir/rmdir/link; successful setattr/security/ACL operations invalidate affected attr/access/ACL state.
- Read/write RPC prepare chooses a fresh read/write stateid and rejects bad contexts. Completion callbacks detect stateid-expired/old/openmode errors and restart if local current stateid differs from the one sent.
- NFSv4.0 client identity uses `SETCLIENTID` and `SETCLIENTID_CONFIRM`; NFSv4.1+ identity uses `EXCHANGE_ID`, optional SP4_MACH_CRED negotiation, `CREATE_SESSION`, slot table setup, connection binding/trunk probing, and periodic `SEQUENCE` lease renewal.

## State and Data Structures

- `nfs_client` state touched here includes clientid, exchange flags, seqid, owner id, acceptor string, last renewal time, session pointer/state, server owner/scope/implementation IDs, state-protection mode flags, recovery flags, transport/trunking state, and lock waitqueue.
- `nfs_server` state is populated with server caps, supported attr bitmasks, no-label bitmasks, cache-consistency bitmasks, exclusive-create bitmasks, ACL masks, fh expiry type, fsid, pNFS block size/layout driver, case-sensitivity flags, and delegation timestamp/open argument capabilities.
- `nfs4_state` carries open/delegation stateids, mode counters (`n_rdonly`, `n_wronly`, `n_rdwr`), open/lock/delegation flags, lock-state lists, waitqueues, owner references, seqlock, and state locks. Updates are serialized with owner locks, seqlocks, RCU, waitqueues, and state locks.
- Per-RPC callback payloads include `nfs4_opendata`, `nfs4_closedata`, `nfs4_createdata`, `nfs4_delegreturndata`, `nfs4_lockdata`, `nfs4_unlockdata`, `nfs4_sequence_data`, `nfs4_get_lease_time_data`, and `nfs4_reclaim_complete_data`.
- Attribute bitmasks are actively adjusted. `nfs4_bitmap_copy_adjust` suppresses delegated attributes from GETATTR-like requests; `nfs4_bitmask_set` adds invalidated attributes back for cache-consistency requests and masks them by server support.
- ACL cache state lives in `NFS_I(inode)->nfs4_acl`, with length-only uncached entries for large ACLs and inline kmalloc-backed entries for small ACL data.

## Dependencies and Integration Points

- SUNRPC integration is pervasive: `rpc_run_task`, `rpc_call_sync`, `rpc_wait_for_completion_task`, `rpc_restart_call_prepare`, `rpc_sleep_on`, `rpc_delay`, transport release, xprt iteration, trunk add/remove, auth flavor handling, and credential references.
- NFS core integration includes inode/fh/fattr helpers, access-cache helpers, open/lock context helpers, state owner and seqid allocation, attr generation/cache invalidation, dentry verifier/splice handling, revalidation, state-manager scheduling, and delegation APIs.
- NFSv4 modules used include `nfs4_fs.h`, `delegation.h`, `callback.h`, `pnfs.h`, `netns.h`, `sysfs.h`, `nfs4idmap.h`, `nfs4session.h`, `nfs40.h`, `nfs42.h`, and `nfs4trace.h`.
- pNFS is referenced throughout via layoutget-on-open, layoutreturn-on-close/delegreturn, data-server write/commit clients, layout driver selection, layout invalidation, and state-protection cleanup bits, but the main layout operation implementations continue after this chunk.
- Security integration includes Linux LSM security-label initialization/release, `security_ismaclabel`, optional `CONFIG_NFS_V4_SECURITY_LABEL`, auth-flavor probing, SECINFO fallback, and SP4_MACH_CRED state-protection negotiation.
- VFS/locking integration includes dentries, inodes, `struct file_lock`, generic file leases, POSIX/flock lock validation, inode locking/rwsem, dcache alias pruning, xattr handler methods, and page/folio buffers.

## Risks and Subtle Behaviors

- Stateid ordering is fragile. The client relies on server stateid seqids and local seqlock/waitqueue ordering to serialize concurrent OPEN, CLOSE, OPEN_DOWNGRADE, LOCK, and LOCKU state transitions.
- Protocol errors are intentionally hidden from userspace after recovery attempts. Unknown or internal NFSv4 errors are often mapped to generic errno values such as `-EIO`.
- Async cancellation paths are correctness-sensitive. Release callbacks may need to close successfully opened state or unlock successfully acquired locks if the local RPC wait was cancelled.
- Delegations change behavior across many paths: opens and locks can be cached locally, attrs can be suppressed from GETATTR, timestamps can be returned during delegation return, and incompatible/revoked delegations trigger state recovery or explicit returns.
- Attribute cache correctness depends on exact bitmask decisions. Requesting too few attrs risks stale metadata; requesting unsupported/delegated attrs can cause avoidable server failures or larger replies.
- Session recovery is tightly coupled to SEQUENCE errors. Bad/misordered sequence handling can restart calls, probe sequence state, drain slots, release transports, and wake slot-table waiters.
- Recovery/delay loops can be long-lived. Soft-error mounts bound some `NFS4ERR_DELAY` retransmissions, but state-manager, grace, lease moved, and clientid busy paths can continue until recovery completes or fatal signal/exit interrupts.
- The `nfs4_lock_delegation_recall` loop compares one condition against `-NFSERR_GRACE` after checking `-NFS4ERR_GRACE`; this looks suspicious and should be verified against surrounding NFS error constants before classification.
- This chunk ends mid-function at `nfs4_free_reclaim_complete_data`, so the `RECLAIM_COMPLETE` cleanup/runner logic is incomplete within this chunk.

## Cross-Chunk References

- Lines 9527-10750 continue `nfs4_free_reclaim_complete_data`, finish `RECLAIM_COMPLETE`, and cover the remaining pNFS layout, stateid test/free, minor-version operation tables, client ops, and xattr handler registration.
- Forward declarations in this chunk for `nfs41_test_stateid` and `nfs41_free_stateid` are used by expired/revoked state cleanup but implemented after this range.
- pNFS calls made here, including open layoutget parsing, layoutreturn-on-close/delegreturn, layout driver setup, and write/commit data-server handling, require the later chunk and `pnfs.*` files for full behavior.
- NFSv4.2-specific helpers referenced here, such as `nfs42_proc_getxattr`, `nfs42_proc_setxattr`, `nfs42_proc_listxattrs`, `nfs42_proc_removexattr`, and READ_PLUS support, are implemented in NFSv4.2-specific source files or later registration code.
- Final per-file synthesis should merge this report with chunk 2 rather than treating this chunk as a complete view of `nfs4proc.c`.

### Chunk 2: lines 9527-10750

# Chunk Research: sources/os/linux/linux-stable/fs/nfs/nfs4proc.c lines 9527-10750

## Scope

This chunk covers the tail of the Linux NFSv4 client procedure implementation. It includes NFSv4.1 reclaim-complete, pNFS `LAYOUTGET`/`LAYOUTRETURN`/`GETDEVICEINFO`/`LAYOUTCOMMIT`, `SECINFO_NO_NAME` root security probing, `TEST_STATEID`/`FREE_STATEID`, NFSv4.1/v4.2 minor-version tables, VFS inode/xattr wiring, server cloning, swap hooks, and `nfs_v4_clientops`.

## APIs and Entry Points

- `nfs41_proc_reclaim_complete()` issues `NFSPROC4_CLNT_RECLAIM_COMPLETE`.
- `nfs4_proc_layoutget()` sends `LAYOUTGET`, handles pNFS-specific errors, and returns a layout segment or `ERR_PTR`.
- `nfs4_proc_layoutreturn()` sends `LAYOUTRETURN`, optionally async, with pNFS cleanup state protection.
- `nfs4_proc_getdeviceinfo()` wraps `GETDEVICEINFO` in exception retry logic and is GPL-exported.
- `nfs4_proc_layoutcommit()` sends `LAYOUTCOMMIT` sync or async and updates inode WCC attributes on release.
- `nfs41_find_root_sec()` resolves root auth flavor via `SECINFO_NO_NAME`, falling back to older probing.
- `nfs41_test_stateid()` and `nfs41_free_stateid()` implement NFSv4.1 stateid validation/freeing.
- `nfs_v4_minor_ops[]`, `nfs_v4_clientops`, inode ops, and xattr handlers publish the client’s operation tables.

## Control Flow

`LAYOUTGET` binds a sequence slot, runs an async RPC task, waits for completion, then converts server responses into local retry/fallback behavior. `LAYOUTUNAVAILABLE` becomes `-ENODATA`, `BADLAYOUT` becomes `-EOVERFLOW`, layout conflicts become retryable, and revoked/expired/bad stateids trigger either open-state recovery or local layout invalidation.

`LAYOUTRETURN` tolerates many cleanup failures. It may exit early for invalid layouts, retries transient network/session/delay errors, refreshes old stateids where possible, and otherwise often clears protocol failure status so local cleanup can proceed.

`SECINFO_NO_NAME` first tries integrity-protected machine credentials when possible, then falls back to the current filesystem RPC client on `WRONGSEC` or unavailable integrity. Root security probing filters returned flavors against mount auth policy.

The end of the chunk is table-driven: minor-version ops wire recovery/session/renewal/migration helpers, VFS inode ops expose NFSv4 directory/file behavior, and xattr handlers expose ACL/DACL/SACL/security-label/user attributes depending on config.

## State, Dependencies, Risks

Session state flows through `seq_args`/`seq_res`; pNFS state flows through layout headers, stateids, ranges, layout segments, and commit/return data. Retry state is carried by `struct nfs4_exception`.

Key dependencies include SUNRPC task APIs, `nfs4_procedures[]`, NFSv4 sequence/session helpers, pNFS layout helpers, state recovery helpers, RPC auth flavor mapping, VFS inode operations, LSM xattr listing, and NFSv4 ACL/user xattr helpers.

Notable risks:
- `nfs41_free_stateid()` increments `cl_count` before allocation/task failure paths that do not visibly drop the reference.
- Async `FREE_STATEID` marks the local stateid freed immediately after task submission.
- `LAYOUTRETURN` intentionally suppresses many failures, which can hide server-side return failure.
- `nfs4_proc_layoutcommit()` replaces flags with `RPC_TASK_ASYNC`, dropping the initial `RPC_TASK_MOVEABLE`.
- `nfs4_listxattr()` checks aggregate size only after calling all producers.

## Cross-Chunk References

Earlier chunks define most functions installed into `nfs_v4_clientops`, the NFSv4.0 minor ops table, reclaim-complete callbacks immediately preceding this range, state recovery helpers wired here, and ACL/security-label/user-xattr implementations exposed by this chunk. The final per-file report should merge this with prior `nfs4proc.c` chunk research.
