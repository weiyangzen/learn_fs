# sources/user-network-fs/samba/source3/winbindd/idmap_rid.c

## Purpose
This deterministic backend maps between a domain SID's RID and Unix IDs using arithmetic: `unix_id = rid - base_rid + low_id`. It does not allocate or persist mappings.

## Important APIs, Types, And Functions
`struct idmap_rid_context` stores `base_rid`. `idmap_rid_initialize` reads `idmap config <domain> : base_rid`. `idmap_rid_id_to_sid` composes a SID from `dom->dom_sid` and computed RID. `idmap_rid_sid_to_id` extracts a RID and computes the Unix ID. Batch wrappers are `idmap_rid_unixids_to_sids` and `idmap_rid_sids_to_unixids`. `idmap_rid_init` registers the backend.

## Control Flow
Initialization allocates private context. ID-to-SID checks the Unix ID range, rejects missing domain SID, composes the SID with RID `id - low_id + base_rid`, marks `ID_TYPE_BOTH`, and sets mapped. SID-to-ID extracts RID, computes ID, sets `ID_TYPE_BOTH`, and range-filters the result.

## State And Persistence
Only `base_rid` is stored in memory. The mapping is derived from domain config and the domain SID supplied by the idmap subsystem.

## Dependencies And Integration
It depends on idmap config, `idmap_unix_id_is_in_range`, SID compose/extract helpers, and idmap registration. It is usually configured per trusted domain.

## Risks And Test Signals
Test low/high boundary IDs, `base_rid` nonzero, IDs below `low_id`, RIDs below `base_rid` causing uint32 underflow, null domain SID, and SID values outside configured range. The batch functions log unexpected errors but return OK, so per-map status assertions are essential.
