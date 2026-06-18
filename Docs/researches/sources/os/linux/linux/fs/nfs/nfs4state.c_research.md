# File Research: sources/os/linux/linux/fs/nfs/nfs4state.c

## Purpose

`nfs4state.c` implements the Linux NFSv4 client-side state model. It owns client ID establishment, state owner caching, open and lock state objects, stateid selection for I/O, sequence-id serialization, asynchronous state recovery, lease renewal, session reset, migration recovery, and reactions to NFSv4.1 sequence status flags.

The file is the recovery coordinator for NFSv4 stateful protocol objects. Other NFS modules perform individual RPCs, delegation operations, pNFS layout work, or VFS open/lock paths, but this file decides when the client must renew, reclaim, purge, reset, migrate, or retry state.

## Key Data and Constants

- `zero_stateid`, `invalid_stateid`, and `current_stateid` provide globally visible special stateids with explicit NFSv4 stateid type annotations.
- `nfs_clid_init_mutex` serializes client-id and trunking discovery setup.
- State owners are stored per `nfs_server` in an RB tree keyed by credential and an LRU list for released owners.
- Open state is represented by `struct nfs4_state`, linked both from the inode and from the credential-specific state owner.
- Lock state is represented by `struct nfs4_lock_state`, linked from an open state and tied into VFS `file_lock` private operations.
- Client recovery is driven by bits in `nfs_client->cl_state`, including lease expiration, reclaim modes, session reset, bind-connection, migration, delegation expiration, and manager scheduling flags.

## Client ID and Lease Establishment

- `nfs4_init_clientid()` performs NFSv4.0 `SETCLIENTID` and `SETCLIENTID_CONFIRM`, records `cl_clientid` and `cl_confirm`, and schedules state renewal after confirmation.
- `nfs41_init_clientid()` performs NFSv4.1+ `EXCHANGE_ID` and `CREATE_SESSION`, starts reboot reclaim when the server did not report an already-confirmed exchange, then marks the client ready.
- `nfs4_setup_state_renewal()` optionally fetches lease time via `nfs4_proc_get_lease_time()`, updates the lease period, and schedules renewal.
- `nfs4_get_machine_cred()`, `nfs4_get_renew_cred()`, and `nfs4_get_clid_cred()` provide credentials for lease, renewal, and client-id operations, preferring machine credentials and falling back to credentials from active state owners where appropriate.
- `nfs4_root_machine_cred()` is a fallback path used during trunking discovery to force root credentials by clearing the configured machine principal.

## Session Draining and Reset

Session-related recovery uses slot table draining to keep in-flight operations from racing with lease, reclaim, session, or transport changes:

- `nfs4_drain_slot_tbl()` marks a slot table draining and waits for active slots to complete.
- `nfs4_begin_drain_session()` drains the legacy client slot table or both NFSv4.1 backchannel and forechannel slot tables.
- `nfs4_end_drain_session()` clears draining flags and wakes waiters.
- `nfs4_reset_session()` destroys and recreates an NFSv4.1 session, handling dead/bad sessions as successful destroy outcomes and routing other errors through recovery error handling.
- `nfs4_bind_conn_to_session()` sends `BIND_CONN_TO_SESSION`, retries on delay, and clears or restores the bind-connection state bit.
- `nfs41_finish_session_reset()` clears lease-confirm/session-reset/bind flags, schedules renewal, and is used after successful session creation or reset.

## State Owner Lifecycle

State owners are credential-scoped open owners:

- `nfs4_get_state_owner()` first searches the per-server RB tree under `cl_lock`; if absent, it allocates and inserts a new owner with a unique owner id.
- `nfs4_find_state_owner_locked()` and `nfs4_insert_state_owner_locked()` compare credentials with `cred_fscmp()` and remove reused owners from the LRU.
- `nfs4_put_state_owner()` decrements the owner refcount and places zero-reference owners on `state_owners_lru` with an expiry timestamp.
- `nfs4_gc_state_owners()` frees expired LRU entries after the server lease window, preserving recently used owner identities to avoid unnecessary `OPEN_CONFIRM` and to avoid quick uniquifier reuse.
- `nfs4_purge_state_owners()` and `nfs4_free_state_owners()` detach and free cached owners at unmount or during reclaim scans.
- `nfs4_reset_state_owner()` refreshes an owner create time after bad sequence-id handling so the server treats subsequent opens as a new sequence.

## Open State Lifecycle

Open state tracks the aggregate read/write mode and per-open counters for one inode plus one state owner:

- `nfs4_get_open_state()` finds an existing valid open state under RCU or creates one, attaches it to the inode open-state list and owner open-state list, increments the owner refcount, and takes an inode reference.
- `nfs4_state_set_mode_locked()` updates the active mode and reorders the owner list so writable states are reclaimed before read-only states.
- `nfs4_put_open_state()` detaches the state from inode and owner lists, returns delegations on close, drops inode and owner references, and frees the state via RCU.
- `__nfs4_close()` decrements mode-specific counters, computes the new aggregate mode, decides whether an RPC `CLOSE` is required, and either drops local state or calls `nfs4_do_close()`.
- `nfs4_close_state()` and `nfs4_close_sync()` expose asynchronous and synchronous close wrappers.

## Lock State and Stateid Selection

The file integrates NFSv4 byte-range lock ownership with Linux VFS file locks:

- `nfs4_get_lock_state()` finds or allocates a lock state for a VFS lock owner and marks the parent open state as using lock state.
- `nfs4_put_lock_state()` drops lock-state references, clears `LK_STATE_IN_USE` when the list empties, and delegates initialized lock-state freeing to minor-version operations.
- `nfs4_set_lock_state()` attaches NFSv4 lock-state ownership to a VFS `file_lock` using `nfs4_fl_lock_ops`; copied locks increment and released locks decrement the NFS lock-state refcount.
- `nfs4_copy_lock_stateid()` selects an initialized matching lock stateid for POSIX or flock/OFD owners, returning `-EIO` for lost locks and `-ENOENT` when no initialized lock state exists.
- `nfs4_copy_open_stateid()` safely snapshots an open stateid using a seqlock.
- `nfs4_select_rw_stateid()` chooses the stateid for read/write I/O in priority order: lock stateid, delegation stateid, then open stateid. For NFSv4.1+ stateid-capable servers it zeroes the seqid field before use.

## Sequence ID Handling

NFSv4.0 open/close/lock operations require serialized sequence-id mutation:

- `nfs4_init_seqid_counter()` initializes owner or lock seqid counters, wait queues, and list heads.
- `nfs_alloc_seqid()`, `nfs_release_seqid()`, `nfs_free_seqid()`, and `nfs_wait_on_sequence()` allocate, queue, wake, and free per-operation seqid wait records.
- `nfs_increment_seqid()` increments only after success or after protocol-defined mutating errors, avoiding increment for non-mutating errors.
- `nfs_increment_open_seqid()` resets the state owner on bad seqid and skips seqid mutation for session-based clients.
- `nfs_increment_lock_seqid()` applies the same mutation rules for lock owners.

## Recovery Scheduling

The state manager is a per-client asynchronous worker:

- `nfs4_schedule_state_manager()` sets `NFS4CLNT_RUN_MANAGER`, takes module and client references, and starts `nfs4_run_state_manager()` unless a manager is already running. It has special handling for swap-backed RPC clients via `NFS4CLNT_MANAGER_AVAILABLE`.
- `nfs4_clear_state_manager_bit()` clears `NFS4CLNT_MANAGER_RUNNING` and wakes client wait queues.
- `nfs4_schedule_lease_recovery()`, `nfs4_schedule_stateid_recovery()`, `nfs4_schedule_session_recovery()`, `nfs4_schedule_migration_recovery()`, and `nfs4_schedule_lease_moved_recovery()` set the relevant state bits and wake the manager.
- `nfs4_wait_clnt_recover()` waits for manager completion and reports client construction failure.
- `nfs4_client_recover_expired_lease()` loops bounded recovery attempts while lease-expired/check-lease bits remain set.

## Reclaim Marking and Recovery

The file supports two recovery modes:

- Reboot/grace recovery uses `NFS_STATE_RECLAIM_REBOOT`, `NFS_OWNER_RECLAIM_REBOOT`, and `NFS4CLNT_RECLAIM_REBOOT`.
- No-grace recovery uses `NFS_STATE_RECLAIM_NOGRACE`, `NFS_OWNER_RECLAIM_NOGRACE`, and `NFS4CLNT_RECLAIM_NOGRACE`.

Important flows:

- `nfs4_state_start_reclaim_reboot()` marks delegations and valid open states for reboot reclaim.
- `nfs4_state_start_reclaim_nograce()` marks delegations for expiry testing and open states for no-grace reclaim.
- `nfs4_reset_seqids()` clears open and lock state flags before reclaiming, ensuring stateids and lock initialization are rebuilt.
- `nfs_inode_find_state_and_recover()` finds open, open-stateid, lock-stateid, and delegation state matching a reported bad/stale stateid and schedules no-grace recovery.
- `nfs4_reclaim_locks()` walks POSIX and flock lock lists, recovering locks and marking unrecoverable locks lost where the server denies or cannot reclaim them.
- `nfs4_reclaim_open_state()` iterates marked open states, calls minor-version recovery operations to recover opens and locks, marks failed open contexts bad when necessary, and tracks lost locks.
- `nfs4_do_reclaim()` drains the session, purges cached owners, scans all superblocks and state owners, runs open-state reclaim, handles recoverable errors, frees purged owners, probes local I/O support, and reports lost locks.
- `nfs4_state_end_reclaim_reboot()` clears reboot reclaim, destroys all pNFS layouts, sends `RECLAIM_COMPLETE` when available, and re-arms reboot reclaim if connection binding is still required.

With `CONFIG_NFS_V4_2`, `nfs42_complete_copies()` also completes server-side copy waiters when the recovered state matches source or destination copy state.

## Lease, Purge, and Error Handling

- `nfs4_check_lease()` chooses renewal credentials, sends the minor-version lease renewal operation, preserves check-lease on timeout, and routes protocol errors through `nfs4_recovery_handle_error()`.
- `nfs4_establish_lease()` drains the session and establishes a client ID through the reboot recovery operations.
- `nfs4_reclaim_lease()` re-establishes the lease after expiration, switches to no-grace reclaim on server-scope mismatch, and otherwise schedules reboot reclaim.
- `nfs4_purge_lease()` establishes a new lease, clears purge-state, marks the lease expired, and forces no-grace reclaim.
- `nfs4_handle_reclaim_lease_error()` centralizes client-id establishment error policy for stale IDs, client-ID-in-use, delay/retry conditions, unsupported minor versions, no space, and unrecoverable exchange failures.
- `nfs4_recovery_handle_error()` maps protocol errors to recovery actions such as callback path repair, no-grace reclaim, lease expiration, session reset, and bind-connection retry.

## Migration and Trunking

- `nfs41_discover_server_trunking()` uses `EXCHANGE_ID` and `nfs41_walk_client_list()` to detect trunking and schedules purge or lease confirmation based on exchange flags and transparent state migration possibility.
- `nfs4_discover_server_trunking()` serializes trunking detection, retries transient errors, falls back from machine principal to root credentials on first access error, and can switch authentication to `RPC_AUTH_UNIX` for certain security/client-ID conflicts.
- `nfs4_schedule_migration_recovery()` validates persistent file handles, marks the server in transition, sets client `MOVED`, and schedules the manager.
- `nfs4_try_migration()` fetches `fs_locations`, drains the session, calls `nfs4_replace_transport()`, and marks migration failure on error.
- `nfs4_handle_migration()` walks servers marked in transition and attempts transport replacement.
- `nfs4_handle_lease_moved()` probes each mounted FSID with `nfs4_proc_fsid_present()` and migrates the server that reports `NFS4ERR_MOVED`.

## Sequence Status Flag Handling

`nfs41_handle_sequence_flag_errors()` is the external entry point for server status flags returned by `SEQUENCE`. Outside recovery, it maps flags to actions:

- restart reclaim needed -> `nfs41_handle_server_reboot()`
- all state revoked -> `nfs41_handle_all_state_revoked()`
- some/admin state revoked -> `nfs41_handle_some_state_revoked()`
- lease moved -> `nfs4_schedule_lease_moved_recovery()`
- recallable state revoked -> destroy layouts and test delegations
- backchannel fault -> session reset
- callback path down -> bind connection to session

When called during recovery, it suppresses reclaim/revocation reactions that are expected to persist until recovery completes, but still handles callback/backchannel faults.

## State Manager Main Loop

`nfs4_state_manager()` is the file's core coordinator. It runs under `memalloc_nofs_save()` to avoid reclaim/writeback deadlocks and repeatedly processes client state bits in priority order:

1. purge state
2. expired lease
3. session reset
4. bind connection to session
5. lease check
6. migration
7. lease moved
8. reboot reclaim plus pNFS layout reboot handling
9. expired delegation detection
10. no-grace reclaim
11. pending delegation returns and recall-any layout returns

On failure it traces `nfs4_state_mgr_failed`, logs a rate-limited warning, marks initial client readiness errors for network-down or invalid states, sleeps for retryable errors, drains sessions, and clears the manager-running bit. `nfs4_run_state_manager()` wraps this loop in a kthread, supports swapper availability waiting, handles signals, drops the client ref, and exits via `module_put_and_kthread_exit()`.

## Cross-File Relationships

- Uses NFSv4 minor-version operations from `clp->cl_mvops` for client ID establishment, lease renewal, reboot/no-grace recovery, lock freeing, and trunking detection.
- Calls NFSv4 RPC helpers such as `nfs4_proc_setclientid()`, `nfs4_proc_exchange_id()`, `nfs4_proc_create_session()`, `nfs4_proc_destroy_session()`, `nfs4_proc_get_locations()`, `nfs4_proc_fsid_present()`, and `nfs4_proc_bind_conn_to_session()`.
- Coordinates with delegation code through `nfs_delegation_mark_reclaim()`, `nfs_mark_test_expired_all_delegations()`, `nfs_reap_expired_delegations()`, delegation stateid matching/recovery, and client delegation returns.
- Coordinates with pNFS through layout destruction, reboot layout handling, recall-any layout return, and migration-related transport replacement.
- Emits `nfs4_state_mgr`, `nfs4_state_mgr_failed`, and `nfs4_state_lock_reclaim` tracepoints declared in `nfs4trace.h`.

## Concurrency and Safety Notes

- `cl_lock`, owner `so_lock`, inode `i_lock`, state `state_lock`, RCU, seqlocks, refcounts, atomics, wait queues, and bit waiters are all used in distinct ownership domains.
- State owner RB-tree operations require `cl_lock`; open-state list mutation uses owner and inode locks; lock-state list mutation uses state lock.
- Open states are freed with RCU because inode open-state lookup can occur under RCU.
- Recovery drains session slots before operations that invalidate session, transport, or state assumptions.
- The manager uses module and client references to keep code and client memory alive while the kthread runs.

## Research Notes

This file should be read as the NFSv4 client state machine rather than ordinary request logic. Most RPC details are delegated to protocol operation tables; the main value here is ordering, retry policy, state marking, and coordination among leases, stateids, sessions, delegations, pNFS layouts, migration, and VFS locks.
