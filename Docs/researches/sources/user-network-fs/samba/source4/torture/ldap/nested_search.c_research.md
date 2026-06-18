# sources/user-network-fs/samba/source4/torture/ldap/nested_search.c

## Purpose

`nested_search.c` tests that Samba's LDAP-backed LDB layer can safely issue a nested search from within an outer search callback. It targets RootDSE and compares selected naming-context attributes from the nested result with the outer result.

## Important APIs, Types, and Functions

- `struct nested_search_context` holds the torture context, root DN, LDB context, and accumulated outer result.
- `nested_search_callback()` forwards replies through `ldb_search_default_callback()` and performs a nested RootDSE search on each entry.
- `test_ldap_nested_search()` builds and executes the outer RootDSE search.
- `torture_assert_res` maps assertion failures to LDB callback errors.

## Control Flow

The test connects to `ldap://<host>/`, creates a NULL RootDSE DN, and builds a base-scope search with callback context. The callback handles entry/done/referral replies, temporarily swaps the request context so the default callback stores the outer reply, then for entry replies runs another base-scope RootDSE search requesting root/config/schema/default naming context attributes. It asserts the nested result has one entry and that each nested element also exists in the outer stored message with matching flags and value counts.

## State and Persistence Behavior

The test is read-only. It stresses client-side request/callback state and context switching rather than server persistence.

## Dependencies and Integration Points

It uses LDB request/callback APIs, LDAP-backed `ldb_wrap_connect()`, command-line credentials, and the LDAP torture suite. The test is registered as `ldap.nested-search`.

## Risks and Edge Cases

The nested search assumes the outer result has already been stored before element comparison, which depends on default callback ordering. It compares flags and value counts but not full value contents. Callback error handling must avoid leaking or corrupting request context when nested operations fail.

## Test Signals

Passing requires the outer search to complete, the nested RootDSE search to succeed inside the entry callback, one nested entry to be returned, and requested naming-context attributes to match the outer message's structure.
