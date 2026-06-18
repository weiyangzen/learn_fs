# sources/user-network-fs/samba/source3/winbindd/wb_query_user_list.c

Purpose: async wrapper that returns a null-separated/list string of fully qualified users for a domain by first querying RIDs and then resolving them to names.

Important APIs and types: `wb_query_user_list_send/recv`; `struct wb_query_user_list_state`; `wbint_RidArray`, `wbint_Principals`, and `winbindd_domain_ref`.

Control flow: `send` stores a domain ref and calls `dcerpc_wbint_QueryUserRidList_send`. The first callback validates status, gets the live domain from the ref, then calls `dcerpc_wbint_LookupRids_send` with the domain SID. The final callback converts each principal name into a domain-qualified username with `fill_domain_username_talloc` and appends it via `strv_add`. `recv` moves the constructed `users` string vector.

State and persistence: request-local state plus a domain ref that detects stale domain objects. No persistent writes.

Dependencies and integration points: child `QueryUserRidList`/`LookupRids`, `winbindd_domain_ref`, string vector helpers, and list-users command handling.

Risks: user list generation requires two child RPCs; stale domain between them fails the request. `strv_add` return values are mapped from Unix errors. The code assumes `LookupRids` returns principal entries corresponding to requested RIDs.

Test signals: empty domain, normal list, stale domain ref after RID fetch, RID lookup failure, names requiring domain qualification/escaping behavior, and allocation failure paths.
