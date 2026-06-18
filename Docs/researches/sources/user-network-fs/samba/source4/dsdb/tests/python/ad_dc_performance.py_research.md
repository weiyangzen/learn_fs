# sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_performance.py

Purpose: this AD DC performance scenario builds a PID-scoped OU containing users, groups, and memberships, measures common LDAP search patterns, exercises repeated domain joins, and then deletes parts of the data. It is a smaller predecessor to the medley test.

Important APIs/types/functions: `GlobalState` tracks user and link offsets. `UserTests` provides `add_if_possible()`, `_prepare_n_groups()`, `_add_users()`, `_test_join()`, `_test_unindexed_search()`, `_test_indexed_search()`, `_link_user_and_group()`, `_unlink_user_and_group()`, random link helpers, and delete helpers. It uses `SamDB`, `Message`, `MessageElement`, `Dn`, `FLAG_MOD_ADD`, `FLAG_MOD_DELETE`, and `samba_tool`.

Control flow: each test method opens a `SamDB`, creates or reuses OUs, and advances class-level counters. Tests are ordered by numeric names to add 1k batches, link users in several shapes, perform joins and searches, add more users, randomly link users to many groups, then delete groups/users and run a final join. Host normalization and legacy runner handling happen at module tail.

State and persistence behavior: directory objects are intentionally retained across tests in the same run; `add_if_possible()` suppresses duplicate-add errors. There is no complete cleanup of the PID OU, so interrupted runs may leave data behind.

Dependencies and integration points: integrates with Samba's Python test harness, `SamDB` LDB operations, `samba-tool domain join`, the target LDAP/TDB database, and stderr consumers that collect timing output.

Risks: order dependence is high because later tests require earlier user/group counts. Random link tests swallow `LdbError`, so duplicate/invalid modifications can hide details. The tempdir created for joins is removed only after a successful join. Performance output is not converted into pass/fail thresholds.

Test signals: subunit success demonstrates functional survival through the workload; printed timings for indexed and unindexed searches and join duration are the useful regression signal.
