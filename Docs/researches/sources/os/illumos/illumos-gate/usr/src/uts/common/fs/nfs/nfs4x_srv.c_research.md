# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_srv.c

## Purpose

`nfs4x_srv.c` implements server-side NFSv4.1 operation handlers and session helpers layered on the existing NFSv4 server state machinery. It covers EXCHANGE_ID, CREATE_SESSION, DESTROY_SESSION, SEQUENCE, RECLAIM_COMPLETE, DESTROY_CLIENTID, BIND_CONN_TO_SESSION, SECINFO_NO_NAME, TEST_STATEID, FREE_STATEID, BACKCHANNEL_CTL, callback security handling, delegation request conversion, and recallable-state race tracking.

## Main Interfaces

Credential/principal helpers:

- `rfs4_cmp_cred_set`, `rfs4_set_cred_set`, `rfs4_free_cred_set`
- `nfs_clid4_cmp`

Operation handlers:

- `rfs4x_op_exchange_id`
- `rfs4x_op_create_session`
- `rfs4x_op_destroy_session`
- `rfs4x_op_sequence`
- `rfs4x_op_reclaim_complete`
- `rfs4x_op_destroy_clientid`
- `rfs4x_op_bind_conn_to_session`
- `rfs4x_op_secinfo_noname`
- `rfs4x_op_test_stateid`
- `rfs4x_op_free_stateid`
- `rfs4x_op_backchannel_ctl`

Session/replay helpers:

- `rfs4x_sequence_prep`
- `rfs4x_sequence_done`
- `rfs4x_cbcheck`
- `rfs4x_bc_setup`
- `rfs4x_exchange_id_free`

Backchannel and delegation helpers:

- `rfs4x_cbsec_valid`, `rfs4x_cbsec_getuid`, `rfs4x_cbsec_getgid`, `rfs4x_cbsec_init`, `rfs4x_cbsec_fini`
- `nfs4x_share_to_delegreq`
- `rfs4x_rs_record`, `rfs4x_rs_erase`

## Client Identity And EXCHANGE_ID

`rfs4x_op_exchange_id()` implements the RFC 5661 EXCHANGE_ID client-record cases. It validates flags, constructs an `nfs_client_id4` from the client owner and RPC caller address, finds or creates the server client record, handles unconfirmed and confirmed records, detects verifier changes, compares credentials/principals, and returns `CLID_INUSE`, `NOENT`, `NOT_SAME`, `PERM`, or `SERVERFAULT` where appropriate.

The handler stores the credential/principal set on new client records, records clientid information in stable storage, reports non-pNFS server behavior, echoes referral support when requested, rejects SSV state protection as unsupported, and fills server implementation/trunking identity. `rfs4x_exchange_id_free()` releases allocated implementation and server-owner response strings.

## Session Creation And Destruction

`rfs4x_op_create_session()` finds the clientid, rejects expired clients, handles sequence-id replay/misorder cases using the client's contrived sequence/result state, confirms unconfirmed clientids when credentials match, creates the session via `rfs4x_createsession()`, caches the CREATE_SESSION result for replay, increments the client sequence, updates the lease, and releases temporary references.

`rfs4x_op_destroy_session()` validates RFC rules when destroying the same session used by the enclosing SEQUENCE: it must be the final operation in the compound. It then finds the session, enforces state-protection credential checks when required, and calls `rfs4x_destroysession()` with an adjusted reference count.

`rfs4x_op_destroy_clientid()` rejects unknown clientids and clientids with sessions or openowners, otherwise marks the client destroying and closes it.

## SEQUENCE And Replay Cache

`rfs4x_sequence_prep()` runs before normal compound execution. It finds the session, validates slot id, operation count, request size, and sequence id. `check_slot_seqid()` distinguishes new requests, replay-cache hits, in-progress duplicates, false retry, retry of uncached replies, and misordered sequence ids.

On a replay-cache hit, the cached `COMPOUND4res` is copied from the slot and normal execution is skipped. On a new request, the slot is marked in use and any previous recallable-state race marker in the slot is erased.

`rfs4x_op_sequence()` must appear as operation zero. It checks for expired leases, validates response-size limits, starts callback-path pinging when needed, records the active client in compound state, advances the slot sequence id, updates session access time, fills the SEQUENCE result, reports callback path down or revoked recallable state, and renews the client lease.

`rfs4x_sequence_done()` releases the slot after reply encoding. It frees any old cached reply, caches the new reply when `cachethis` is set or when the compound is a solo SEQUENCE, otherwise frees the response. It adjusts the session cached-reply count.

## Backchannel Support

`rfs4x_bc_setup()` creates a backchannel if one is not already established, initializes a backchannel slot table, installs it with an atomic compare-and-swap, and marks that a callback ping is needed.

`rfs4x_op_bind_conn_to_session()` binds a transport connection to the fore or back channel. For backchannel binding it sets a session tag on the transport and registers callback connection metadata with RPC service controls.

`ping_cb_null_thr()` tests callback paths using `CB_NULL` calls over untested connections. It tracks ping-in-progress state, path count, ping count, and failure state under the session DB lock.

`rfs4x_op_backchannel_ctl()` updates callback program/security parameters, flushes stale callback channels, and requests a ping. Only `AUTH_NONE` and `AUTH_SYS` callback security are accepted; RPCSEC_GSS is explicitly not implemented here.

## Stateid Operations

`rfs4x_op_test_stateid()` iterates all supplied stateids, normalizes special stateid forms with `get_stateid4()`, calls `rfs4_get_all_state()`, releases any resolved open/delegation/lock state, and returns per-stateid status codes while the operation status itself is `NFS4_OK`.

`rfs4x_op_free_stateid()` handles stateid classes:

- OPEN stateids are valid but not freed directly here; the result is `NFS4ERR_LOCKS_HELD`.
- LOCK stateids check active locks for the lockowner/sysid and invalidate the lock state if no locks remain.
- DELEG stateids use `rfs4_get_deleg_any()` so revoked delegations can be acknowledged. Revoked delegations are invalidated, the client's revoked-delegation count is decremented, and `NFS4_OK` is returned.
- Invalid or unknown stateid types return `NFS4ERR_BAD_STATEID`.

## Other Operations

`rfs4x_op_reclaim_complete()` marks whole-client reclaim complete and decrements the server reclaim counter when applicable. Per-filesystem reclaim completion is accepted as a no-op because this server does not track that granularity.

`rfs4x_op_secinfo_noname()` performs SECINFO on `.` or `..` for the current directory and clears the current filehandle after a successful result, as required by the protocol.

`nfs4x_share_to_delegreq()` maps NFSv4.1 `OPEN4_SHARE_WANT_*` bits saved by XDR decoding into internal `delegreq_t` values. Compile-time assertions verify the bit layout assumption.

`rfs4x_rs_record()` and `rfs4x_rs_erase()` record and clear recallable delegation state associated with a session/slot/sequence tuple, helping detect races where a delegation is returned/recalled around a cached reply.

## Dependencies

This file depends on:

- Existing NFSv4 client/state DB objects: `rfs4_client_t`, `rfs4_session_t`, openowners, stateids, delegations, leases, stable storage.
- Session allocation/destruction in `nfs4x_state.c`.
- Slot/replay-cache state in the session object.
- RPC service controls for callback channel binding.
- Lock manager interfaces for active lock checks.

## Research Notes

This file is the behavioral center of the illumos NFSv4.1 server. The main correctness risks are EXCHANGE_ID case handling, clientid/session lifetime races, sequence-id replay-cache behavior, slot cleanup timing after reply encode, callback path state transitions, and FREE_STATEID handling for revoked delegations and active locks.
