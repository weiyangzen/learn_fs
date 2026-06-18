# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_state.c

## Purpose

`nfs4_state.c` implements the illumos NFSv4 server state engine: client IDs, open owners, lock owners, open stateids, lock stateids, file state, delegation state, lease expiry, stable storage recovery, distributed stable storage path handling, and export teardown cleanup. The file is the stateful protocol core beneath the NFSv4 server operations, with the explicit lock hierarchy documented near the top: `client > openowner > state > lo_state > lockowner > file`, and with database hash bucket locks above the object locks they protect.

## Main Responsibilities

- Maintains protocol sentinel stateids: all-zero, all-one, current-stateid, and invalid-stateid, plus helpers to save/resolve NFSv4.1 current stateid in a compound request.
- Provides a general `rfs4_state_wait_t` single-active waiter primitive used by state owners to serialize replay-sensitive operations.
- Deep-copies and frees cached `OPEN` and `LOCK` replies, including denied lock owner buffers and delegation ACL strings.
- Initializes and tears down global kmem caches for each state object class and per-zone NFSv4 state databases/tables.
- Reads, writes, moves, removes, and validates stable-storage client records under the default and distributed stable storage directories.
- Creates and searches state database entries through multiple indices: NFS client identity, server clientid, client IP, open owner, lock owner, lock owner pid, vnode/file, stateid, owner+file, file, delegation client+file, and delegation stateid.
- Enforces NFSv4 lease expiry, stateid generation/sequence validation, cluster node ID embedding, grace-period reclaim eligibility, and state cleanup during client close, file remove, and unexport.

## Key Data and Tables

- Global `kmem_cache_t *` caches: `rfs4_client_mem_cache`, `rfs4_clntIP_mem_cache`, `rfs4_openown_mem_cache`, `rfs4_openstID_mem_cache`, `rfs4_lockstID_mem_cache`, `rfs4_lockown_mem_cache`, `rfs4_file_mem_cache`, `rfs4_delegstID_mem_cache`, `rfs4_session_mem_cache`.
- Per-zone tables created in `rfs4_state_zone_init()`:
  `rfs4_client_tab`, `rfs4_clntip_tab`, `rfs4_openowner_tab`, `rfs4_state_tab`, `rfs4_lo_state_tab`, `rfs4_lockowner_tab`, `rfs4_file_tab`, `rfs4_deleg_state_tab`, plus NFSv4.1 extended state via `rfs4x_state_init_locked()`.
- Clientids/stateids encode server start time and database IDs. In clustered boots, the low-level ID fields embed `clconf_get_nodeid()` and reject foreign node IDs through `foreign_clientid()` / `foreign_stateid()`.
- Stable storage entries store `NFS4_SS_VERSION`, client verifier, and client owner byte string; record leaf names are derived from client address plus server-generated clientid.

## Stable Storage and Recovery Flow

The stable-storage code supports NFSv4 reclaim after restart and HA-style distributed stable storage.

- `rfs4_dss_setpaths()` unpacks an nvlist provided by `nfssys()` and records the active DSS paths, preserving a previous set as old paths across warm starts.
- `rfs4_state_zone_init()` creates a new server instance with either the default path or default plus DSS paths, then initializes the state database and calls `rfs4_ss_init()`.
- `rfs4_ss_init()` reads default stable storage by calling `rfs4_dss_readstate()`, then enables future stable-storage writes.
- `rfs4_dss_readstate()` reads oldstate in place and reads state while moving entries into oldstate. This builds the current server instance's reclaim list.
- `rfs4_ss_getstate()` validates state files by type, readability, size, version, and encoded client-id length; malformed/empty files may be removed.
- `rfs4_ss_chkclid()` searches oldstate from the current server instance backward through active grace instances and marks `rc_can_reclaim` when a client owner matches. Expired instances have oldstate cleared.
- `rfs4_ss_clid()` writes a client stable-storage record after SETCLIENTID/confirmation activity, and `rfs4_ss_clid_write()` writes to all paths of all active instances until client grouping is improved.
- Client expiry/removal marks `rc_ss_remove`; `rfs4_client_destroy()` removes the stable-storage leaf from every DSS path when needed.

## State Object Lifecycle

Clients are created by `rfs4_client_create()`, which allocates a server clientid, copies the client-provided owner and address, initializes callback state, open-owner/session lists, credentials, lock-manager sysid state, server-instance association, and NFSv4.1 contrived sequence state. Lookup is by client owner (`rfs4_findclient()`) or server clientid (`rfs4_findclient_by_id()`), with special handling for replacing old unconfirmed clients.

Open owners are keyed by `{clientid, owner bytes}`. `rfs4_openowner_create()` looks up the parent client, copies the owner, initializes the cached reply, sequence id, waiter, and per-owner state list, and links the owner into the client. `rfs4_update_open_sequence()` and `rfs4_update_open_resp()` maintain replay state for the owner.

Lock owners are similarly keyed by `{clientid, owner bytes}` and also indexed by generated `pid`. `rfs4_lockowner_create()` holds the parent client and assigns `rl_pid` from the database entry ID. Lock-owner destruction frees owner bytes and releases the client.

File entries are keyed by vnode and may also be cached in vnode-specific data under `nfs4_srv_vkey`. `rfs4_file_create()` holds the vnode, copies the filehandle, initializes delegation info, share counters, recall condition variable, and per-file rwlock. Lookup can use the table or the vnode VSD fast path; `rfs4_findfile_withlock()` also returns with the file rwlock held and retries if the vnode disappeared.

Open state entries are keyed by stateid and also indexed by openowner+file and file. Creation holds the file and open owner, generates an OPENID stateid, initializes the lostate list, and links into the open owner. Destruction removes from the owner, destroys lock-state list, releases share locks if still open, and drops file/owner references.

Lock state entries connect a lock owner to an open state. Creation derives a LOCKID stateid from the open state, adds the lock owner pid, initializes sequence/reply/wait state, and links into the open state's `rs_lostatelist`. Destruction removes kernel locks via local `cleanlocks()` or cluster-aware `lm_remove_file_locks`, frees cached reply, and releases lock owner and open state.

Delegation state entries are keyed by client+file and by delegation stateid. Creation holds the file and client, creates a DELEGID stateid, records grant time, and starts as `OPEN_DELEGATE_NONE`. Expiry deliberately preserves revoked delegations as live protocol objects awaiting `FREE_STATEID`; destruction returns the delegation, adjusts revoked counts, and releases references.

## Stateid Validation and Access Control

The file centralizes stateid error mapping and sequence checks:

- `rfs4_check_clientid()` maps stale/expired clientids using server start time and cluster node ID.
- `what_stateid_error()` maps absent stateids to `STALE_STATEID`, `BAD_STATEID`, or `EXPIRED`, with delegation-specific revoked/removed behavior.
- `rfs4_get_state()`, `rfs4_get_state_nolock()`, `rfs4_get_lo_state()`, `rfs4_get_deleg_state()`, and `rfs4_get_all_state()` retrieve referenced state while rejecting foreign cluster stateids and expired leases.
- `rfs4_check_stateid_seqid()` and `rfs4_check_lo_stateid_seqid()` return internal classification values for bad, old, replay, expired, unconfirmed, closed, and OK stateids.
- `check_state_seqid()` implements NFSv4.1 session semantics where a seqid of zero is accepted.
- `rfs4_check_stateid()` is the main read/write path validator. It handles zero/one special stateids, delegation recalls and `NFS4ERR_DELAY`, grace-period rejection, stateid/filehandle matching, open-owner confirmation, closed state, access mode checks, delegation write tracking, lease refresh, and caller context filling for nbmand checks.
- `rfs4_state_has_access()` enforces OPEN share access for reads/writes and checks file deny-read counters when the current state did not grant read access.

## Cleanup Paths

- `rfs4_client_close()` invalidates a client, removes all open state and NFSv4.1 sessions, then releases the client reference.
- `rfs4_free_opens()` closes each state for an open owner and optionally invalidates the state/open owner.
- `rfs4_close_all_state()` invalidates a file entry, closes every open state referring to it, clears vnode VSD, and releases the vnode; this is used when remove-like operations must force state teardown after delegations are handled.
- `rfs4_clean_state_exi()` is called during unexport and walks lock-state, open-state, delegation-state, and file tables for filehandles under the export. It closes/invalidate matching state and clears vnode/delegation hooks. The comments explicitly note this may run from global-zone unexport code against non-global-zone structures, so it uses the passed `nfs_export_t`/`nfs4_srv_t` rather than zone-specific lookup.

## Dependencies and Integration Points

- Depends on the generic `rfs4_database`/`rfs4_table`/`rfs4_index`/`rfs4_dbe_*` state database layer.
- Integrates with NFSv4 protocol state from `nfs4.h`, `nfs4_state.h`, NFS export data, vnode/VOP primitives, lock manager APIs, DTrace probes, cluster node configuration, CPR callbacks, and NFSv4.1 session helpers (`rfs4x_*`, `rfs4_has_session()`).
- Stable storage uses kernel vnode file I/O (`vn_open`, `VOP_READ`, `VOP_WRITE`, `VOP_READDIR`, `vn_rename`, `vn_remove`) and nvlist unpacking for DSS path configuration.
- Delegation cleanup interacts with FEM monitors (`deleg_rdops`, `deleg_wrops`) and vnode open downgrade paths.

## Concurrency and Locking Notes

The implementation relies on strict reference-before-lock behavior. Most public lookup functions return held database entries that must be released through the matching `rfs4_*_rele()` routine, and some variants also return with file rwlocks held. Stable storage server-instance traversal uses `servinst_lock` and per-instance `oldstate_lock`; client lookup replacement uses `rfs4_findclient_lock` to hide an old client while searching. Vnode VSD access is guarded by `v_vsd_lock`, while file-level state operations use `rf_file_rwlock` to serialize teardown and lookup.

## Risks and Edge Cases

- Stable-storage code intentionally ignores many I/O failures and may remove malformed files; correctness depends on conservative validation and robust DSS path configuration.
- `rfs4_ss_has_client()` appears intended to prevent double-counting clients in oldstate. The body continues on byte-equal client IDs and returns true on byte-different IDs after equal length, which is surprising and worth reviewing against historical fixes.
- Many hash functions are simple shift/add or pointer-address hashes; correctness is maintained by compare functions, but distribution may matter under high state counts.
- `rfs4_state_zone_fini()` warns that consumers may still be active while database tables are destroyed; teardown ordering is a known sensitivity.
- Cluster encoding assumes table IDs leave enough high bits for node IDs and asserts this rather than handling overflow dynamically.
- Several paths hold locks across `KM_SLEEP` allocations because structure sizes come from locked objects. The comments acknowledge this as difficult to avoid.

## Testing and Verification Signals

Useful tests would exercise SETCLIENTID/CONFIRM replay, server restart reclaim from stable storage, DSS path failover, lease expiry and clear-locks forced expiry, open/lock replay reply caching, special zero/one/current stateids, NFSv4.1 session seqid-zero behavior, delegation revocation plus `FREE_STATEID`, file remove/unexport cleanup, and clustered foreign clientid/stateid rejection.
