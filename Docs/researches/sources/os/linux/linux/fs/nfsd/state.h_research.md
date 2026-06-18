# File Research: sources/os/linux/linux/fs/nfsd/state.h

## Summary
Defines the core NFSv4 state model used by NFSD: client IDs, sessions, callbacks, stateids, delegations, open/lock owners, files, pNFS layout state, blocked locks, recovery records, and copy-notify state.

## Main Responsibilities
- Defines wire-derived identifiers such as `clientid_t`, `stateid_t`, and copy stateids.
- Describes NFSv4 callback infrastructure and callback operation hooks.
- Defines common stateid objects and concrete delegation, open/lock, and layout stateid containers.
- Defines client/session/channel/slot structures for NFSv4.0 and v4.1+ session operation.
- Models openowners, lockowners, replay caches, per-client open/delegation file state, file aggregation, blocked locks, and pNFS layout state.
- Declares lifecycle and lookup functions implemented by NFSv4 state code.

## Key Data Structures and Interfaces
- `struct nfs4_stid` is the common refcounted stateid core for open, lock, delegation, and layout state.
- `struct nfs4_client` is the top-level client object containing identity, credentials, callbacks, sessions, stateid IDR, delegations, reclaim state, async copies, nfsdfs entries, and optional pNFS/SCSI layout data.
- `struct nfsd4_session` tracks v4.1+ session IDs, channel attributes, connections, backchannel slots, and forward replay slots.
- `struct nfs4_stateowner`, `nfs4_openowner`, and `nfs4_lockowner` model seqid-mutating owners and replay state.
- `struct nfs4_file` aggregates all state for a filehandle/inode, including cached `nfsd_file` references, share deny/access counts, delegations, and layout state lists.
- `struct nfs4_ol_stateid`, `nfs4_delegation`, and `nfs4_layout_stateid` specialize stateid behavior for opens/locks, delegations, and pNFS layouts.

## Important Behavior
Stateid status bits encode closed, revoked, admin-revoked, freeable, and freed states. Locking rules differ by type: client locks protect open/lock state, delegation locks protect delegation status, and layout locks protect layout status.

Delegations carry recall callback state, retry counts, delegated timestamp fields, CB_GETATTR state, and per-client/per-file linkage. Helper predicates distinguish read, write, and attribute delegations.

Sessions bound resource limits with constants for max slots, slot cache size, and total memory per session. Slots store seqid, cached status/data, credential, generation, and flags for in-use/cache/reuse behavior.

Clients can be active, courtesy, or expirable. Courtesy clients preserve state after lease expiry until conflict or laundromat pressure forces expiration.

Replay support exists both for NFSv4.0 owner seqid operations and NFSv4.1+ session slots. `NFSD4_REPLAY_ISIZE` embeds a common-size reply buffer and falls back to dynamic allocation for large replies.

pNFS layout stateids include layout lists, recall callback, delayed fence work, exponential backoff state, and fenced status.

## Dependencies
Depends on crypto MD5, IDR, refcounts, SunRPC transports, filehandle definitions, NFSD service definitions, callbacks, pNFS optional configuration, nfsd file cache objects, and NFSv4 XDR/state operation implementations.

## Risks and Subtleties
This header encodes the ownership and lock hierarchy for NFSv4 state. Bugs usually come from using the wrong lock for a stateid type, dropping references too early, or bypassing lookup/preprocess helpers that validate generation, type, status, client, filehandle, and open mode.

Many structs require first-field embedding so `container_of()` conversions work. Layout, delegation, open, and lock state objects depend on these layout assumptions.

Client lifetime is intentionally nontraditional: resting clients can have zero active references while still present in lookup tables, and destruction must respect in-flight compounds, callbacks, sessions, and reclaim records.
