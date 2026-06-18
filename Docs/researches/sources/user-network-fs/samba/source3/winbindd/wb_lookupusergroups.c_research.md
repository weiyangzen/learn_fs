# sources/user-network-fs/samba/source3/winbindd/wb_lookupusergroups.c

Purpose: implements async user group SID lookup for a single user SID, with a cache-first path before dispatching to the relevant domain child.

Important APIs and types: `wb_lookupusergroups_send/recv`; `struct wb_lookupusergroups_state` stores the copied user SID and returned `wbint_SidArray`.

Control flow: `send` copies the input SID, checks `lookup_usergroups_cached`, and completes immediately on a cache hit. On cache miss it finds the domain with `find_domain_from_sid_noinit`, fails with `NT_STATUS_NO_SUCH_DOMAIN` if absent, then calls `dcerpc_wbint_LookupUserGroups_send`. The callback merges RPC transport/result errors and completes. `recv` moves returned group SIDs to the caller and logs them at info level.

State and persistence: group membership can be satisfied from winbind cache. The async request itself owns only transient talloc state and a copied SID.

Dependencies and integration points: depends on security/SID helpers, cache lookup, domain discovery, and generated `wbint_LookupUserGroups` child RPC. Used by higher-level `GETUSERDOMGROUPS`/group membership request paths and by ADS/MSRPC backend method implementations.

Risks: domain discovery uses the copied user SID; unknown domains fail before backend fallback. Cache correctness directly affects returned memberships. A cache hit avoids domain contact and returns request-posted completion, so callers must handle both synchronous-posted and asynchronous completions.

Test signals: cache hit, cache miss success, unknown-domain failure, RPC failure, and ownership of moved SID arrays. Membership tests should include primary group and nested/alias behavior at higher layers.
