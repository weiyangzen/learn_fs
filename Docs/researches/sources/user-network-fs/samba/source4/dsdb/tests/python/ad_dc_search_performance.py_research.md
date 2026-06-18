# sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_search_performance.py

Purpose: this focused performance script creates users and groups, then stresses LDAP filter evaluation for indexed, unindexed, complex, `member`, and `memberOf` searches over linked and unlinked directory data.

Important APIs/types/functions: `UserTests` implements OU setup, `_add_users()`, `_add_users_ldif()`, `_prepare_n_groups()`, `_test_unindexed_search()`, `_test_indexed_search()`, `_test_complex_search()`, `_test_member_search()`, `_link_user_and_group()`, and `_test_link_many_users()`. It uses `itertools.product` to build a search-expression space, `random.sample()` to bound it, and LDB modify/search APIs for link setup and timing.

Control flow: after parsing host/credentials, each test opens `SamDB`, creates PID-scoped OUs if needed, and uses class-level `GlobalState` offsets to build a cumulative data set. Early tests add 1k users and measure searches, middle tests add more users via LDIF and normal adds, then link users to group 0 plus another group before repeating search workloads.

State and persistence behavior: test data persists for the process run and is not cleaned up automatically. Link state is not tracked in a set, so duplicate link attempts would surface as LDB errors, although the deterministic link pattern avoids most duplicates.

Dependencies and integration points: depends on Samba `SamDB`, LDB `Message`/`MessageElement`, LDAP search scopes, Samba test runner compatibility, and stderr timing collection.

Risks: all performance checks are wall-clock printouts without thresholds. Search samples are deterministic because the random seed is reset, but server data from previous runs can still affect timings if PID OUs collide or cleanup is incomplete. Complex filters include comparison operators that can stress parser and index behavior differently across backends.

Test signals: successful completion plus timing lines for each filter family provide regression evidence for AD search performance.
