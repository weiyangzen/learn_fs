# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/unique_object_sids.c

Purpose: This LDB module enforces uniqueness for local-domain `objectSID` values by marking eligible `objectSID` elements with `LDB_FLAG_INTERNAL_FORCE_UNIQUE_INDEX`. It allows duplicate SIDs for foreign security principals and replication-conflict records, where duplicates are valid or tolerated.

Important APIs, types, and functions: `struct private_data` stores the local domain SID. `message_contains_local_objectSID` decodes `objectSID` from a request message and checks it with `dom_sid_in_domain`. `flag_objectSID` shallow-copies a message and ORs the force-unique flag on the copied element. `unique_object_sids_add` and `unique_object_sids_modify` wrap add/modify requests when needed. `unique_object_sids_init` loads the domain SID from `samdb_domain_sid` and registers private data.

Control flow: On add, the module checks whether the message contains a local-domain objectSID. If not, it forwards the original request. If yes, it shallow-copies the message, flags the copied `objectSID`, builds a new add request with the original controls and callback, and passes the new request down. On modify, it performs the same local-SID detection but first requires `DSDB_CONTROL_REPLICATED_UPDATE_OID`; without that control it rejects the modify with `LDB_ERR_UNWILLING_TO_PERFORM`. Initialization calls `ldb_next_init`, allocates private data, and logs a warning if the domain SID is unavailable, as can happen during provisioning.

State and persistence behavior: Persistent database effects are indirect: the forced unique-index flag influences lower LDB/index behavior for local objectSID values. The module itself stores only the local domain SID pointer in private data and does not modify the original request message.

Dependencies and integration points: It depends on Samba SID parsing helpers, `samdb_result_dom_sid`, `samdb_domain_sid`, LDB request builders, DSDB callbacks, and the replicated-update control. It integrates with lower database/index modules that interpret `LDB_FLAG_INTERNAL_FORCE_UNIQUE_INDEX`.

Risks: If the domain SID is unavailable, local uniqueness enforcement is disabled with only a warning. Because the message copy is shallow, the element structure is copied but underlying values are shared; this is intentional for flag mutation but ownership must remain valid for the request lifetime. Non-replicated objectSID modification is blocked to preserve integrity, so callers that legitimately need SID changes must use the replication path.

Test signals: `test_unique_object_sids.c` covers local versus foreign SIDs, missing objectSID pass-through, request-copy behavior, original-request immutability, replicated modify success, and non-replicated modify rejection.
