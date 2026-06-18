# sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_owner.c

Purpose: Implements the NFSv4 state-owner cache for open owners, lock owners, and the embedded clientid owner, plus NFSv4.0 seqid/replay tracking and lock-conflict response helpers.

Important APIs, types, and functions: The `ht_nfs4_owner` table stores `state_owner_t` entries keyed by owner type, clientid, and opaque owner value. Key functions are `Init_nfs4_owner`, `create_nfs4_owner`, `free_nfs4_owner`, `display_nfs4_owner`, `compare_nfs4_owner`, `Process_nfs4_conflict`, `Release_nfs4_denied`, `Copy_nfs4_denied`, `Copy_nfs4_state_req`, and `Check_nfs4_seqid_locked`.

Control flow: `create_nfs4_owner` builds a stack key with owner name, client record, owner type, related open owner, initial seqid, confirmation state, and cached response placeholders, then delegates allocation/deduplication to `get_state_owner`. `init_nfs4_owner` initializes the per-owner state list, refs the related owner and clientid, and links open or lock owners into the client's per-client list under `cid_mutex`. Existing lock owners can be re-associated with a new related open owner when they have no active POSIX locks, recovering zombie lock-owner reuse after client crash/expiry. `free_nfs4_owner` removes per-client linkage and releases cached response and references. Seqid handling compares a request to the next expected seqid, returns cached responses on replay, and flags bad seqids for out-of-order or wrong-op requests.

State and persistence behavior: Owner state is in-memory hash/cache state. It stores owner opaque bytes, clientid, seqid, confirmation flag, related owner, cached response, cached request op, last object pointer, state list, and optional open-owner cache expiry. There is no direct persistence; owners are rebuilt from clients and protocol operations, and recovery is managed through clientid/recovery files.

Dependencies and integration points: Integrates with generic state-owner cache routines in `sal_functions`, clientid refs, NFS protocol compound copy/free helpers, response-size accounting, `LOCK4denied` encoding, and `unknown_owner`. The owner lists are consumed by `nfs4_state.c` and client expiry logic.

Risks: Hashing is intentionally simple and marked for replacement, so collision behavior relies on compare correctness. Replay detection stores shallow object pointers for last entry and only selected arguments, which is sufficient for current semantics but fragile if reused for deeper operation matching. Related-owner repair must not mask genuine active-lock conflicts. `Process_nfs4_conflict` allocates denied owner buffers conditionally, so release/copy paths must preserve the `unknown_owner` sentinel.

Test signals: Exercise new and reused open/lock owners, per-client list linkage, related-owner mismatch with active versus no locks, seqid next/replay/bad cases, cached response copying, lock denied owner allocation/release/deep-copy, and owner cleanup on client expiry.
