
# sources/user-network-fs/nfs-ganesha/src/SAL/state_deleg.c

## Purpose

`state_deleg.c` implements NFSv4 delegation state management in SAL. It decides when delegations can be granted, acquires/releases FSAL leases, tracks delegation heuristics and client/file statistics, handles conflicts and recalls, persists revoked delegation file handles, and tracks revoked stateids until clients free them.

## Important APIs, types, and functions

- Globals: `g_total_num_files_delegated` and `g_max_files_delegatable` enforce a server-wide file delegation limit.
- Revocation state: `revoked_delegations_list` and `revoked_delegations_lock` track revoked delegation stateids for later `NFS4ERR_DELEG_REVOKED` responses and `FREE_STATEID` cleanup.
- `init_new_deleg_state()` initializes `union state_data` for a new delegation.
- `do_lease_op()`, `acquire_lease_lock()`, and `release_lease_lock()` bridge SAL delegation state to FSAL `lease_op2()`.
- `update_delegation_stats()`, `deleg_heuristics_recall()`, `init_deleg_heuristics()`, and `reset_cbgetattr_stats()` maintain file/client counters and CB_GETATTR state.
- `should_we_grant_deleg()` applies configuration, FSAL capability, export permission, callback-channel, reclaim, contention, client-revocation, open-mode, and global-limit checks.
- `deleg_supported()` and `can_we_grant_deleg()` perform additional support and lock/anonymous-operation checks.
- Revoked-state APIs include `has_revoked_delegations_for_client()`, `atomic_remove_revoked_and_clear_flags()`, `mark_sessions_have_revoked_delegations()`, `remove_revoked_stateid()`, and `is_stateid_revoked()`.
- `deleg_revoke()` and `state_deleg_revoke()` perform revocation, FSAL lease release, stable-storage revoke recording, session marking, and state deletion.
- `state_deleg_conflict_impl()`/`state_deleg_conflict()` detect conflicting operations and start async delegation recall.
- `is_write_delegated()` and `handle_deleg_getattr()` support write delegation GETATTR and conflict behavior.

## Control flow

Delegation grant starts with support checks: server config, regular-file object type, FSAL read/write delegation capabilities, export permissions, confirmed owner rules, and reclaim claim types. `should_we_grant_deleg()` then handles callback-channel-down reclaim cases, recent recalls, clients with repeated revokes, write-open contention, and the global files-delegated limit. `can_we_grant_deleg()` separately denies grants when anonymous operations or conflicting NLM locks exist. If a grant proceeds, `acquire_lease_lock()` maps delegation type to `FSAL_DELEG_RD` or `FSAL_DELEG_WR`, calls FSAL `lease_op2()`, updates stats, and clears CB_GETATTR state.

On recall or revoke, `deleg_heuristics_recall()` decrements file/client counters, resets file delegation type when no delegations remain, updates average hold time, and clears CB_GETATTR state. `deleg_revoke()` obtains state owner/export refs, builds an NFSv4 file handle, adds the stateid to the revoked list, releases the FSAL lease, persists the revoked file handle through `nfs4_record_revoke()`, marks v4.1 sessions as having revoked delegations, deletes state, and releases references/context.

Conflict detection scans active delegation states under `STATELOCK`. Write operations conflict unless the current client is the only delegate. Read operations conflict with another client's write delegation. Conflicts start `async_delegrecall()` and return true so callers can delay/deny the operation.

For GETATTR on a write-delegated file, `handle_deleg_getattr()` checks per-file CB_GETATTR state. It returns success for completed callback, delay while in progress or after sending a new callback, and falls back to delegation recall on callback failure or scheduling failure.

## State and persistence behavior

Most delegation state is in memory on `state_t`, `state_owner_t`, `state_hdl`, `file_deleg_stats`, client counters, and session flags. Persistent behavior occurs only for revoked delegations: `deleg_revoke()` calls `nfs4_record_revoke()`, which uses the selected recovery backend to store the revoked file handle so a post-restart `DELEG_PREV` can be rejected.

The revoked stateid list is process-local and protected by a mutex. It remains until `FREE_STATEID` or explicit removal. For NFSv4.1, session `has_revoked_delegations` flags are set on revoke and cleared when no revoked entries remain.

## Dependencies and integration points

The file depends on FSAL delegation lease support, NFSv4 OPEN/claim semantics, export permissions, callback RPC scheduling (`async_delegrecall`, `async_cbgetattr`), server statistics (`inc_grants`, `dec_grants`), file-handle conversion, recovery revocation recording, state list locking, and op context management. It is used by OPEN, stateid validation, lock/share conflict paths, lease expiry cleanup, and callback handling.

## Risks and edge cases

- `has_revoked_delegations_for_client()` ignores its `clientid` parameter and returns true if any revoked delegation exists globally, so per-client status may be over-reported.
- `atomic_remove_revoked_and_clear_flags()` checks whether the global list is empty, not whether the same client still has revoked delegations, which can keep or clear session flags incorrectly in multi-client scenarios.
- `add_to_revoked_delegations()` uses `malloc()` while `atomic_remove_revoked_and_clear_flags()` uses `gsh_free()` and `remove_revoked_stateid()` uses `free()`, a mixed allocator pattern worth auditing.
- Grant limit accounting increments before the final grant path and relies on recall decrement; failed later paths must avoid leaking the global count.
- Conflict detection uses `state->state_owner` directly while scanning; caller-held locks must protect this relationship.
- CB_GETATTR support is marked TODO and defaults to recall on failure; deployment behavior may be conservative.

## Test signals

Delegation tests should cover read/write grants, mixed read-write opens, export and FSAL capability denial, callback channel down with reclaim claims, recent recall starvation prevention, clients with repeated revokes, global delegation limit accounting, NLM lock conflicts, anonymous operation conflicts, FSAL lease failures, write delegation conflict with same vs different client, CB_GETATTR state transitions, revoke persistence, v4.0 vs v4.1 session flag behavior, `FREE_STATEID` cleanup, and restart `DELEG_PREV` rejection through recovery records.
