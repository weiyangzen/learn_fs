# sources/user-network-fs/samba/source4/dsdb/tests/python/large_ldap.py

Purpose: this LDAP stress suite verifies Samba behavior for very large result sets, large attributes, iterator search error propagation, IOV/result size boundaries, and query timeout enforcement.

Important APIs/types/functions: `ManyLDAPTest.setUpClass()` creates one OU with 2000 child OUs and `test_unindexed_iterator_search()` iterates 2001 matching results through `search_iterator()`. `LargeLDAPTest.setUpClass()` creates 200 users with 2 MiB `jpegPhoto` values and distinct DACLs. `test_unindexed_iterator_search()` and `test_iterator_search()` compare small-attribute searches with searches that exceed response size limits. `test_timeout()` temporarily lowers `MaxQueryDuration` in the default query policy and verifies an expensive OR filter times out.

Control flow: fixtures are class-scoped for cost reasons. Tests first require an LDAP URL, then stream iterator replies, assert each reply is an `ldb.Message`, call `result()` where expected, and catch `LdbError` for size/time limit cases. Timeout testing modifies `lDAPAdminLimits`, opens a fresh connection so limits reload, runs a slow filter, and relies on `addCleanup()` to restore the policy message.

State and persistence behavior: class setup creates large persistent objects under randomized OUs and class teardown tree-deletes them. Timeout testing mutates a configuration policy and restores the original `lDAPAdminLimits` via cleanup.

Dependencies and integration points: depends on LDAP transport, `SamDB.search_iterator`, LDB size/time limit errors, `sd_utils` for per-object DACL churn, default query policy layout, and server-side chunking behavior.

Risks: resource intensive: roughly hundreds of MiB of attribute payload plus DACL work. Old Samba may drop sockets, so teardown recreates the connection. One size-limit path documents a client bug where the second iterator exception may not be raised, so the test accepts partial results instead of failing.

Test signals: exact counts for small searches, partial counts plus `ERR_SIZE_LIMIT_EXCEEDED` for oversized `jpegPhoto` searches, successful 100-result chunked large-attribute search, `ERR_TIME_LIMIT_EXCEEDED`, and duration bounded around the configured timeout.
