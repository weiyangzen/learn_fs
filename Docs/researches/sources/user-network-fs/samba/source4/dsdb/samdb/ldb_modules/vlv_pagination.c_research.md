# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/vlv_pagination.c

## Purpose
`vlv_pagination.c` implements Samba's LDB Virtual List View module. It handles the LDAP VLV request control by caching a sorted search result as object GUIDs, serving requested windows, and returning VLV response controls with a context ID for follow-up requests.

## Important APIs, Types, and Functions
`struct results_store` stores one cached VLV search: context ID, timestamp, GUID array, referrals, lower controls, copied VLV/sort details, and returned controls. `struct private_data` owns a fixed-size cache of `VLV_N_SEARCHES` stores per module connection. `struct vlv_context` binds an active request to a store. Core helpers are `new_store`, `vlv_search_by_dn_guid`, `save_referral`, `send_referrals`, `vlv_gt_eq_to_index`, `vlv_calc_real_offset`, `vlv_results`, `vlv_search_callback`, `copy_search_details`, `vlv_copy_down_controls`, `vlv_search`, `vlv_request_init`, and `ldb_vlv_init`.

## Control Flow and Behavior
`vlv_search` passes through requests without the VLV control. With VLV, it requires a server-sort control and clears VLV criticality locally. A zero-length context ID starts a new lower search that asks only for `objectGUID`, lets the normal sort control order those GUID-bearing entries, strips VLV/sort and ASQ from later per-GUID lookups, and collects entries in `vlv_search_callback`. A non-empty context ID searches the per-connection cache and either serves the cached result, passes through unknown noncritical cookies, or returns `LDAP_UNAVAILABLE_CRITICAL_EXTENSION` for unknown critical cookies.

`vlv_results` computes the target index either from a by-offset request using the Windows-compatible `vlv_calc_real_offset` formula or from a greater-than-or-equal assertion using binary search over the cached sorted GUIDs. It re-fetches each visible row by `<GUID=...>` using the original requested attributes, sends entries, appends a VLV response control, and reports target position/content count.

## State and Persistence Behavior
The module keeps volatile per-LDB-module cache state only. `VLV_N_SEARCHES` limits the number of concurrent cached searches per connection; `new_store` reuses empty slots or evicts the oldest timestamp. The cache stores GUIDs and control copies, not full entry payloads. Returned context IDs are process-local little memory copies of incrementing `uint32_t` values and are not durable across connections, process restarts, or module reinitialization.

## Dependencies and Integration Points
The module integrates with LDB search callbacks, VLV request/response controls, server-side sort controls, ASQ behavior, Samba GUID extraction, LDAP error codes, binary search helpers, and normal DSDB lower-module search behavior. It is built as the `ldb_vlv` module in `wscript_build_server` and registered with `ldb_vlv_init`.

## Risks and Edge Cases
The cache can become stale between the original GUID search and later page windows; missing entries are skipped and the window may be extended by one when possible. Greater-than-or-equal mode assumes the sort attribute exists and has at least one value in the per-GUID lookup; absent values would dereference an empty element. `vlv_copy_down_controls` allocates `num_ctrls` pointers but writes a NULL terminator after filtered controls; when no controls are filtered this requires room for `num_ctrls + 1`, so allocation size is a point to audit. Context ID comparison uses raw in-memory `uint32_t` bytes, which is fine intra-process but not portable as an external format. Unknown noncritical cookies silently fall through to the lower stack. The fixed cache size can evict active client cookies under concurrent use.

## Test Signals
Tests should cover no-VLV pass-through, VLV without sort failure, initial search and follow-up cookie flow, unknown cookie critical/noncritical behavior, by-offset edge cases including 0/0, denominator 0, denominator 1, and offset beyond end, greater-than-or-equal forward and reverse sorting, referral forwarding, stale/deleted objects, ASQ control stripping, cache eviction, and control preservation in final replies.
