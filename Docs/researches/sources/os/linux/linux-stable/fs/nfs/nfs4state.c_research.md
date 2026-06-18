# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4state.c

## Purpose

`nfs4state.c` implements the client-side NFSv4 state model and recovery engine. It owns clientid/session establishment, state owner caching, open state and lock state lifetime, stateid selection, seqid serialization, lease renewal, server reboot recovery, no-grace recovery, migration recovery, session reset/bind recovery, delegation/layout recall dispatch, and the asynchronous NFSv4 state-manager thread.

Despite the header comment saying "Client-side XDR", this file is not an XDR codec file in practice; it is the core NFSv4 client state machine.

## Major Concepts

- `nfs_client`: server/client instance whose `cl_state` bitset drives asynchronous recovery.
- `nfs_server`: mounted export/superblock state linked from `clp->cl_superblocks`.
- `nfs4_state_owner`: per-credential open owner, stored in an rb-tree on `server->state_owners` and cached on `state_owners_lru`.
- `nfs4_state`: per-inode/per-owner open state, linked from both inode open-state lists and owner open-state lists.
- `nfs4_lock_state`: per-lock-owner state under an open state.
- `nfs_seqid_counter` and `nfs_seqid`: serialize NFSv4.0 open/lock operations that require sequence IDs.
- `clp->cl_mvops`: minor-version specific operations used for establish/reclaim/renew flows.
- `NFS4CLNT_*` bits: state-manager work queue encoded in the client state bitset.

## Static Stateids and Client ID Initialization

The file defines three special stateids:
- `zero_stateid`: all-zero special stateid.
- `invalid_stateid`: invalid all-`0xff` style stateid.
- `current_stateid`: special current-stateid value.

For NFSv4.0, `nfs4_init_clientid()` performs `SETCLIENTID` then `SETCLIENTID_CONFIRM`, stores `cl_clientid` and `cl_confirm`, and manages `NFS4CLNT_LEASE_CONFIRM`.

For NFSv4.1+, `nfs41_init_clientid()` performs `EXCHANGE_ID` then `CREATE_SESSION`; if the server did not report an already-confirmed client, it starts reboot reclaim. `nfs41_finish_session_reset()` clears lease-confirm/session-reset/bind flags and schedules lease renewal.

`nfs41_discover_server_trunking()` uses `EXCHANGE_ID` and `nfs41_walk_client_list()` to detect whether a new transport is trunked to an existing client. If no trunking match is found, it may mark state for purge or lease confirmation depending on transparent state migration possibility.

## Credentials

The preferred credential path is machine credentials:
- `nfs4_get_machine_cred()` returns `rpc_machine_cred()`.
- `nfs4_get_renew_cred()` first tries machine credentials, then scans superblocks and state owners for an open-state credential.
- `nfs4_get_clid_cred()` also returns machine credentials.

`nfs4_root_machine_cred()` forcibly clears GSS principal data, used as a fallback during trunking discovery after access failure.

## Session Slot Draining

Several recovery operations require no in-flight session traffic. The helpers are:
- `nfs4_drain_slot_tbl()`: marks a slot table draining and waits if slots are in use.
- `nfs4_begin_drain_session()`: drains backchannel and forechannel slot tables, or legacy `cl_slot_tbl`.
- `nfs4_end_drain_session()`: clears draining and wakes slot waiters.

This protects session reset, lease establishment, migration transport replacement, and delegation expiration handling from racing active RPC traffic.

## State Owner Lifetime

State owners are keyed by credentials:
- `nfs4_find_state_owner_locked()` searches `server->state_owners`.
- `nfs4_insert_state_owner_locked()` inserts or reuses an existing owner.
- `nfs4_get_state_owner()` handles lookup/allocation/insertion and triggers LRU garbage collection.
- `nfs4_put_state_owner()` moves refcount-zero owners to `state_owners_lru` instead of immediately freeing them.
- `nfs4_gc_state_owners()` expires LRU owners older than a lease window.
- `nfs4_purge_state_owners()` detaches cached owners at unmount/reclaim boundaries.
- `nfs4_free_state_owners()` frees a detached list.

The LRU cache matters for NFSv4.0 because keeping owner uniquifiers around avoids unnecessary `OPEN_CONFIRM` and prevents quick reuse of old owner names.

## Open State Lifetime

`nfs4_get_open_state()` finds or allocates a per-inode/per-owner `nfs4_state`, links it under:
- `NFS_I(inode)->open_states`
- `owner->so_states`

`nfs4_put_open_state()` removes those links, returns delegations on close if needed, drops inode and owner refs, and frees via RCU.

`nfs4_state_set_mode_locked()` updates the active read/write mode and reorders owner state list entries so write-capable states appear first. Recovery relies on this ordering to reclaim write/RDWR state before read-only state to reduce unwanted delegation churn.

`__nfs4_close()` decrements read/write/RDWR open counters, computes remaining mode, clears delegation state when fully closed, and either drops local state or sends `CLOSE` via `nfs4_do_close()`.

## Lock State Lifetime and File Lock Integration

Lock state is tracked under `state->lock_states`:
- `nfs4_get_lock_state()` finds or allocates a lock state for an `fl_owner_t`.
- `nfs4_put_lock_state()` removes and frees lock state, using minor-version `free_lock_state()` if initialized on the server.
- `nfs4_set_lock_state()` attaches NFSv4 lock-private state to a Linux `file_lock`.

`nfs4_fl_lock_ops` provides copy/release hooks so file-lock duplication and release keep `nfs4_lock_state` refcounts correct.

`__nfs4_find_lock_state()` can match both POSIX lock owner and flock/OFD owner and deliberately prefers POSIX owner when both are possible.

## Stateid Selection for I/O

`nfs4_select_rw_stateid()` chooses the stateid for read/write:
1. Rejects invalid open state with `-EIO`.
2. Checks lock stateid via `nfs4_copy_lock_stateid()`.
3. If a lost lock is detected, returns `-EIO` without considering delegations.
4. Tries delegation stateid through `nfs4_copy_delegation_stateid()`.
5. Uses a valid lock stateid if one was found.
6. Falls back to open stateid via `nfs4_copy_open_stateid()`.

For servers supporting NFSv4.1 stateid semantics, it zeros `dst->seqid`.

## Seqid Serialization

NFSv4.0 open/close/lock style operations require per-owner sequence ordering:
- `nfs_alloc_seqid()` allocates a queued seqid object.
- `nfs_wait_on_sequence()` adds it to the sequence list and sleeps if it is not first.
- `nfs_release_seqid()` wakes the next queued task.
- `nfs_increment_seqid()` increments the counter for successful operations and seqid-mutating errors, but not for non-mutating errors.
- `nfs_increment_open_seqid()` resets owner create time on `BAD_SEQID` and skips seqid increments for session-based clients.
- `nfs_increment_lock_seqid()` applies lock seqid increment rules.

## Recovery Scheduling APIs

Externally visible scheduling entry points set client/server bits and start the state manager:
- `nfs4_schedule_state_manager()`
- `nfs4_schedule_lease_recovery()`
- `nfs4_schedule_migration_recovery()`
- `nfs4_schedule_lease_moved_recovery()`
- `nfs4_schedule_stateid_recovery()`
- `nfs4_schedule_session_recovery()`

`nfs4_wait_clnt_recover()` waits for the manager to finish. `nfs4_client_recover_expired_lease()` loops manager scheduling until lease recovery bits clear or retry budget is exhausted.

The state manager is started as a kthread named from the server address. It pins the module and client while running. For swap-backed clients it can remain available and sleep waiting for future state-manager work.

## Reclaim Marking

Reclaim flows mark state at several granularities:
- `nfs4_state_mark_reclaim_reboot()`: marks open state for grace-period reboot reclaim unless it was already marked no-grace.
- `nfs4_state_mark_reclaim_nograce()`: marks open state for recovery without server grace.
- `nfs4_state_start_reclaim_reboot()`: sets client reboot reclaim bit, marks delegations, and marks all open states.
- `nfs4_state_start_reclaim_nograce()`: marks expired delegations and all open states no-grace.
- `nfs_inode_find_state_and_recover()`: finds open/lock/delegation state matching a bad stateid and schedules no-grace recovery.
- `nfs4_state_mark_open_context_bad()` and `nfs4_state_mark_recovery_failed()` flag user open contexts as bad after unrecoverable state failures.

`nfs4_clear_open_state()` clears open/delegation flags and lock initialization flags so recovery can rebuild state cleanly.

## Reclaim Execution

`nfs4_reclaim_open_state()` walks an owner's open states with the requested reclaim flag. It:
- skips invalid/closed states,
- rejects server-side copy state under `CONFIG_NFS_V4_2`,
- calls minor-version `recover_open`,
- reclaims locks through `nfs4_reclaim_locks()`,
- marks unrecoverable open contexts bad for local errors,
- converts many server stateid/grace/session errors into no-grace reclaim or manager retry.

`nfs4_reclaim_locks()` walks POSIX and flock lock lists under inode lock context, calls `ops->recover_lock()`, marks locks lost on denial/conflict/memory-style failures, and propagates severe server/session/timeout errors.

`nfs4_do_reclaim()` drains the session, purges cached state owners, walks all superblocks and owners, and invokes `nfs4_reclaim_open_state()`. It handles recoverable errors through `nfs4_recovery_handle_error()` and returns `-EAGAIN` to re-run state-manager work when bits were adjusted.

After successful reboot reclaim, `nfs4_state_end_reclaim_reboot()` clears reboot reclaim, destroys pNFS layouts, sends optional `RECLAIM_COMPLETE`, and re-marks reboot reclaim if the connection is not bound to the session.

## Lease Handling

`nfs4_check_lease()` renews the lease using minor-version state maintenance ops. Timeout re-sets `CHECK_LEASE` without treating the lease as expired. Other errors are normalized through `nfs4_recovery_handle_error()`.

`nfs4_reclaim_lease()` establishes a new client id/session after expiration, sets reboot or no-grace reclaim as appropriate, and clears check/expired bits.

`nfs4_purge_lease()` re-establishes the lease, clears purge state, marks lease expired, and starts no-grace reclaim.

`nfs4_handle_reclaim_lease_error()` centralizes establishment errors: retry on delay/transient errors, mark lease expired, clear lease confirmation for stale clientid, map minor-version mismatch to `-EPROTONOSUPPORT`, and fail client initialization for some hard errors.

## Migration and Lease-Moved Recovery

`nfs4_schedule_migration_recovery()` requires persistent file handles, sets `NFS_MIG_IN_TRANSITION` on the server and `NFS4CLNT_MOVED` on the client.

`nfs4_try_migration()`:
- allocates a page, fs_locations, and fattr,
- calls `nfs4_proc_get_locations()`,
- verifies locations data,
- drains the session,
- calls `nfs4_replace_transport()`,
- marks migration failed on error.

`nfs4_handle_migration()` processes servers marked in transition. `nfs4_handle_lease_moved()` probes root FSIDs with `nfs4_proc_fsid_present()` and migrates the server reporting `NFS4ERR_MOVED`.

## Trunking Discovery

`nfs4_discover_server_trunking()` is process-context trunking detection. It serializes with `nfs_clid_init_mutex`, obtains client-id credentials, calls minor-version `detect_trunking`, and handles:
- transient retry statuses,
- stale clientid retry,
- access failure by trying root machine cred once,
- security fallback to `RPC_AUTH_UNIX`,
- protocol mismatch,
- wrong security/clientid-in-use hard failures.

## Sequence Status Flag Handling

`nfs41_handle_sequence_flag_errors()` reacts to NFSv4.1 `SEQUENCE` status flags:
- restart reclaim needed: server reboot recovery.
- all state revoked: reset all state.
- some/admin state revoked: no-grace recovery.
- lease moved: lease-moved recovery.
- recallable state revoked: destroy layouts and test expired delegations.
- backchannel fault: session reset.
- callback path down: bind connection to session.

If called from recovery, it avoids re-triggering reclaim/state-revoked work but still handles backchannel/callback path faults.

## Session Reset and Binding

`nfs4_reset_session()` destroys and recreates the session. It treats already-dead/bad sessions as acceptable, retries delayed backchannel-busy cases, zeroes the session id before create-session, and finishes with `nfs41_finish_session_reset()`.

`nfs4_bind_conn_to_session()` drains the session, sends `BIND_CONN_TO_SESSION`, clears/re-sets the bind bit on delay, and routes other errors through recovery handling.

## State Manager Main Loop

`nfs4_state_manager()` is the central ordered recovery loop. It runs under `memalloc_nofs_save()` to avoid deadlocks with NFS writeback during reclaim. Each iteration traces current state, clears `RUN_MANAGER`, and processes work in priority order:

1. `PURGE_STATE`: purge lease.
2. `LEASE_EXPIRED`: reclaim lease.
3. `SESSION_RESET`: reset session.
4. `BIND_CONN_TO_SESSION`: bind connection.
5. `CHECK_LEASE`: renew/check lease.
6. `MOVED`: migration.
7. `LEASE_MOVED`: lease moved.
8. `RECLAIM_REBOOT`: recover reboot state, then pNFS reboot layout handling, then reclaim complete.
9. `DELEGATION_EXPIRED`: drain and reap expired delegations.
10. `RECLAIM_NOGRACE`: recover expired/no-grace state.
11. Delegation returns and layoutreturn-any recalls after manager bit is cleared.

Failures are traced with `trace_nfs4_state_mgr_failed()`, rate-limited to the log, and either fail client initialization for selected errors or sleep and retry later.

## Concurrency and Locking

Important locking patterns:
- `clp->cl_lock` protects client/server state-owner trees and client state transitions.
- `owner->so_lock` protects open-state lists and open counters.
- `inode->i_lock` protects inode open-state links.
- `state->state_lock` protects lock-state lists and state flags.
- RCU protects open file and open state list traversal.
- Session slot-table locks and completions gate traffic draining.
- `memalloc_nofs_save()` prevents reclaim/writeback deadlocks during recovery.
- `nfs_clid_init_mutex` serializes trunking/clientid initialization.

## Exports and Cross-File Relationships

Exported symbols include:
- `nfs4_schedule_lease_recovery`
- `nfs4_schedule_migration_recovery`
- `nfs4_schedule_lease_moved_recovery`
- `nfs4_schedule_stateid_recovery`
- `nfs4_schedule_session_recovery`

Tracepoints used here include:
- `trace_nfs4_state_mgr`
- `trace_nfs4_state_mgr_failed`
- `trace_nfs4_state_lock_reclaim`

These are declared in `nfs4trace.h` and instantiated by `nfs4trace.c`.

## Error-Handling Notes

The file distinguishes:
- local errors such as `-ENOMEM`, `-EIO`, `-ESTALE`,
- NFSv4 protocol errors such as `-NFS4ERR_STALE_CLIENTID`, `-NFS4ERR_EXPIRED`, `-NFS4ERR_BADSESSION`,
- retryable transport/session errors such as `-ETIMEDOUT` and `-NFS4ERR_DELAY`.

A key pattern is to translate protocol errors into state-manager bits rather than immediately failing the caller, then return `-EAGAIN` to re-run the manager with the updated work state.

## Research Takeaways

`nfs4state.c` is the NFSv4 client's recovery brain. Normal I/O paths depend on this file for valid stateid selection and lock/open/delegation state tracking. Recovery is bit-driven, asynchronous, and carefully ordered to preserve protocol correctness across server reboot, lease expiration, session loss, migration, callback faults, delegation recall, and pNFS layout state changes.
