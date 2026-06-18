# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_sequence.c

## Purpose
Implements NFSv4.1 SEQUENCE, which establishes session/slot context for a compound, enforces exactly-once sequencing, handles replay cache lookup, reserves the client lease, returns session status flags, and serializes slot use.

## Important APIs, Types, and Functions
- `nfs4_op_sequence` handles `NFS4_OP_SEQUENCE`.
- `check_replay_request` compares the current compound opcode list against the slot's last request for diagnostics when a repeated sequence id is not an actual replay.
- Uses `nfs41_Session_Get_Pointer`, `reserve_lease_or_expire`, `release_nfs4_res_compound`, `release_slot`, `check_resp_room`, `check_session_conn`, `has_revoked_delegations_for_client`, and session/client refcount helpers.
- `nfs4_op_sequence_Free` is a no-op.

## Control Flow
SEQUENCE rejects v4.0, resolves the session, reserves the client lease, preserves a clientid ref in compound data, validates slot id, locks the slot, checks whether the request sequence id is the next expected value, a replay of the previous value, or misordered. For cached replay, it replaces the current compound result with the cached result and returns `NFS_REQ_REPLAY`. For uncached replay it returns `NFS4ERR_RETRY_UNCACHED_REP`; for other mismatches, `NFS4ERR_SEQ_MISORDERED`.

On a new valid request, it records session/sequence/slot in compound data, increments the slot sequence, releases any previous slot cache, fills `SEQUENCE4resok`, sets callback-path and revoked-delegation flags, records `sa_cachethis`, sets `op_ctx->clientid`, verifies response room, checks session connection binding, and deliberately keeps the slot lock held for the rest of compound execution.

## State and Persistence Behavior
Mutates in-memory session slot sequence and cached-result state, preserves client/session refs in compound data, updates the lease reservation, and may clear `session->has_revoked_delegations` after verification. It controls duplicate request cache behavior for the whole compound.

## Dependencies and Integration Points
Integrated with the NFSv4.1 session table, DRC/cached result lifecycle, compound response allocator, client lease management, callback channel state, revoked delegation tracking, and connection binding checks.

## Risks
Slot lock ownership crosses function boundaries; the compound engine must release it after completing/caching the result. Replay response replacement must correctly manage result refs. Misidentifying replay vs misordered requests can cause client hangs. Response-room checks happen after session establishment because max response sizing depends on session attrs.

## Test Signals
Test v4.0 invalid, bad session, expired client, bad slot, next sequence success, cached replay, uncached replay, misordered sequence, opcode mismatch diagnostics, callback path down flag, revoked delegation flag set/cleared, cachethis behavior, and slot lock/release under concurrent compounds.
