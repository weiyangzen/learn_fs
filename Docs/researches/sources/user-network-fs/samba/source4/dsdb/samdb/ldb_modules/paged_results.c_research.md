# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/paged_results.c

## Purpose

`paged_results.c` implements Samba's DSDB LDB module for the LDAP paged-results control. It accepts searches with `LDB_CONTROL_PAGED_RESULTS_OID`, caches the complete result identity set for an initial search, and returns subsequent pages by re-searching each result by GUID. This preserves a stable page sequence while allowing the returned entry content and DN to reflect current database state, matching observed Windows behavior for moved objects.

The module rejects incompatible VLV+simple-paged combinations and registers the paged-results control in rootDSE during initialization.

## Important APIs and Types

`struct private_data` is module-private state. It tracks the next string cookie ID, the count of active result stores, and a doubly linked list of `results_store` objects.

`struct results_store` is the persistent per-cookie page state. It contains the cookie, timestamp, cached referrals, response controls from the initial search, an array of result GUIDs, saved downstream controls, saved requested attrs, current index `last_i`, and a shallow copy/string representation of the original filter.

`struct paged_context` is per-request state holding the original request, page size, selected store, and final controls to return.

Main functions are `new_store()`, `store_destructor()`, `paged_search()`, `paged_search_callback()`, `paged_results()`, `paged_search_by_dn_guid()`, `paged_results_copy_down_controls()`, `paged_controls_same()`, `paged_attrs_same()`, and `paged_request_init()`.

## Control Flow

`paged_search()` first checks for the paged-results control. Requests without it pass through unchanged. It rejects malformed control data and rejects concurrent VLV requests with `LDB_ERR_UNSUPPORTED_CRITICAL_EXTENSION`. Page size is normalized so negative sizes from oversized client values become `0x7fffffff`.

For an initial request with zero-length cookie, a page size of zero is invalid. The module creates a new store, ensures the downstream search includes an extended-DN control so each returned DN contains a GUID component, and sends a downstream search requesting no user attributes. The original filter is shallow-copied into the store and also serialized as a string for continuation validation. Requested attrs and non-paged/non-ASQ controls are copied into the store. `ldb_save_controls()` removes the paged control from the downstream request.

`paged_search_callback()` receives the full initial result set. For each entry it extracts the GUID extended DN component and appends it to a dynamically growing GUID array. Referrals are saved in a linked list. On done, it shrinks the GUID array, saves response controls, calls `paged_results()` to emit the first page, and completes the original request.

For continuation requests, `paged_search()` finds the matching cookie in the store list. It validates that the filter string, non-paged controls, and requested attribute set match the original request. It promotes the store in the LRU list, treats page size zero as abandon/success, and otherwise calls `paged_results()`.

`paged_results()` advances through the cached GUID array until it has sent the requested page size or exhausted the store. Each GUID is re-searched using a BASE search on `<GUID=...>` and the original filter. Missing/deleted entries are skipped without failing the page. Referrals are emitted as soon as possible. The returned paged control contains the cookie and total result count when more pages remain, or an empty cookie when the page sequence is exhausted.

## State and Persistence Behavior

All state is in-memory and talloc-owned by the module. There is no disk persistence and no cross-process cookie sharing. The module caps active stores at 10, matching the default MaxResultSetsPerConn behavior noted in comments; creating the eleventh store frees the list tail. Stores also carry timestamps, but no aging policy is implemented beyond the LRU cap.

Because only GUIDs are cached, page continuation observes current object content and may skip deleted objects. The original filter remains applied during per-GUID rehydration, so entries that no longer match can also disappear from later pages.

## Dependencies and Integration Points

The module depends on LDB request/control APIs, extended DN control, GUID extraction via `GUID_from_ndr_blob()`, Samba linked-list macros, LDAP result/control constants, and talloc ownership. It cooperates with ASQ by excluding ASQ controls from copied continuation controls because ASQ changes search semantics. It uses rootDSE control registration via `ldb_mod_register_control()`.

The module must appear at a point in the LDB stack where the initial search can produce extended DNs with GUID components and where per-GUID searches can re-enter lower modules safely.

## Risks and Edge Cases

The in-memory cookie namespace is per module instance and monotonically increments `uint32_t`; very long-lived processes could wrap cookie IDs. There is no timeout cleanup despite stored timestamps.

Continuation validation uses `ldb_filter_from_tree()` string equality, set-like requested-attribute comparison, and custom control comparison. Differences in semantically equivalent filter serialization or duplicate attrs may affect compatibility. `paged_attrs_same()` checks attrs from the first list are present in the second but does not compare lengths, so duplicate or extra continuation attrs need careful consideration.

The initial search caches all GUIDs before returning the first page, so very large result sets consume memory proportional to the full result count. The GUID array grows by doubling and has overflow protection near `INT_MAX/2`, but the module still has no configurable result-store memory budget.

`paged_results_copy_down_controls()` steals controls/control data into the store. This works with the original request lifetime assumptions but is sensitive to callers that construct unusual non-talloc control trees.

Per-GUID re-searches are synchronous (`ldb_request()` plus `ldb_wait()` per entry), so large pages can incur significant latency and repeated lower-stack work.

## Test Signals

Tests should cover initial and continuation paging, abandon with size zero and non-empty cookie, invalid initial size zero, VLV conflict rejection, changed filter/control/attrs rejection, deleted and moved objects between pages, referral preservation, result count/cookie behavior on final page, LRU eviction after more than 10 active stores, requests lacking extended-DN input control, oversized page sizes, and ASQ interaction. Memory tests should exercise large result sets and store destruction.
