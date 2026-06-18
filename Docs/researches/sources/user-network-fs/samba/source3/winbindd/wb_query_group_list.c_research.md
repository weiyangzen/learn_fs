# sources/user-network-fs/samba/source3/winbindd/wb_query_group_list.c

Purpose: async wrapper around child `QueryGroupList` RPC for retrieving group principals in one domain.

Important APIs and types: `wb_query_group_list_send/recv`; `struct wb_query_group_list_state` with a `wbint_Principals` result.

Control flow: `send` dispatches `dcerpc_wbint_QueryGroupList_send` to the domain child handle. The callback receives RPC status/result and completes. `recv` moves `groups.principals` to the caller and returns `num_groups`.

State and persistence: transient request-local talloc state only.

Dependencies and integration points: generated winbind RPC stubs, `dom_child_handle`, and group enumeration in `wb_next_grent.c`.

Risks: no local retry or fallback; backend/child errors propagate to the enumeration layer, where they may be treated as empty-domain progress. Caller receives only principals, so memory ownership is important.

Test signals: success with zero and nonzero groups, RPC transport failure, operation result failure, and talloc ownership of moved principal arrays.
