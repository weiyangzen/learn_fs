# sources/user-network-fs/samba/source4/dsdb/common/util_groups.c

## Purpose
This file implements nested group expansion for source4 DSDB authentication. Given a DN value, it walks transitive `memberOf` links and accumulates the SIDs and SID attributes that should appear in an authorization token or membership result.

## Important APIs, Types, and Functions
The exported function is `dsdb_expand_nested_groups(struct ldb_context *sam_ctx, struct ldb_val *dn_val, bool only_childs, const char *filter, TALLOC_CTX *res_sids_ctx, struct auth_SidAttr **res_sids, uint32_t *num_res_sids)`. It consumes an extended-DN value, expects SID components in those extended DNs, queries `groupType` and `memberOf`, and appends `struct auth_SidAttr` entries with `SE_GROUP_DEFAULT_FLAGS` plus `SE_GROUP_RESOURCE` when `GROUP_TYPE_RESOURCE_GROUP` is set.

## Control Flow, State, and Persistence
The function initializes the result count when the caller's SID array is NULL, validates that a SAM context exists, parses the input DN from the LDB value, extracts the `SID` extended component, minimizes the DN, and searches the object. With `only_childs=true`, it performs a base `dsdb_search_dn()` that does not add the starting object to the result; otherwise it searches with the caller-supplied filter and considers adding the object's SID before recursing. It tolerates missing SIDs for non-SAM objects and missing objects, including a special fallback for foreignSecurityPrincipal SID-DNs that can fail due to duplicate same-SID objects outside the main domain partition. Duplicate entries are avoided with `sids_contains_sid_attrs()`, but the check is a linear O(n) scan for each candidate. The function is read-only; all state is returned through the caller's talloc-owned SID array.

## Dependencies and Integration
It depends on auth SID attribute structures, LDB DN parsing, DSDB extended-DN SID parsing from `util.c`, `dsdb_search()`/`dsdb_search_dn()`, Samba security flags, and AD group-type constants. It integrates with token construction and membership expansion callers that need domain-local/resource-group attributes and nested `memberOf` traversal in source4 authentication.

## Risks
Recursive traversal can become expensive on deep or dense membership graphs, and duplicate detection is O(n^2) overall. Correct behavior depends on callers requesting `DSDB_SEARCH_SHOW_EXTENDED_DN` so `memberOf` values contain SID components. If corrupt extended DN data is present, the function returns corruption-like NTSTATUS errors and token creation can fail. The foreignSecurityPrincipal fallback intentionally hides some no-such-object cases, which is useful for compatibility but can obscure directory inconsistency.

## Test Signals
Tests should cover a user DN expanded only through parent groups, direct group expansion including the group itself, nested groups with duplicates, domain-local/resource-group SID attributes, foreignSecurityPrincipal fallback by SID, non-SAM objects without SIDs, corrupt extended SID components, filter mismatch returning no SID, missing `sam_ctx`, and deep nesting/performance behavior.
