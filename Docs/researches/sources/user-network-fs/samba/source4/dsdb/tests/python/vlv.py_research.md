# sources/user-network-fs/samba/source4/dsdb/tests/python/vlv.py

## Purpose

`vlv.py` is a comprehensive LDAP integration suite for Virtual List View, server-side sort, paged results, deleted-object visibility, cookie lifetime, and mutation behavior during active views. It compares Samba behavior against expected AD/Windows semantics for sorted and paged searches.

## Important APIs, Types, and Functions

Top-level helpers `encode_vlv_control()` and `get_cookie()` build VLV request controls and parse response cookies. `TestsWithUserOU` creates a test OU tree and synthetic users with locale, binary, numeric, timestamp, Unicode, newline, and special-character attributes. `VLVTestsBase.vlv_search()` performs a sorted VLV search. `VLVTests`, `VLVTestsRO`, and `VLVTestsGC` cover read/write, read-only, and global catalog variants. `PagedResultsTests`, `PagedResultsTestsRO`, `PagedResultsTestsGC`, and `PagedResultsTestsRW` cover paged-results behavior.

## Control Flow

Setup creates `ou=vlvtesttree` and `ou=vlvou`, then populates `N_ELEMENTS` users. VLV tests derive expected ordering from plain server-side sort, then perform offset/count and greater-than-or-equal VLV requests with and without cookies. Mutation tests create, delete, rename, or modify users during an active cookie-backed view and assert the view remains anchored to the original candidate list while visible attributes may update. Paged tests walk multiple concurrent cookies, mutate entries between pages, verify changed expression/control/attribute requests fail with LDAP error 12, and confirm VLV plus paged results is rejected as an unsupported critical extension.

## State and Persistence Behavior

The suite writes a temporary OU tree and many users, then deletes the tree in `tearDown()` unless `--delete-in-setup` defers cleanup to the next run. Cookies are connection-local server state: `test_multiple_searches()` confirms old VLV cookies expire when the per-connection search limit is exceeded and that cookies do not work on a new `SamDB` connection. Paged and VLV tests intentionally mutate directory state while cookies are live to verify snapshot and membership semantics.

## Dependencies and Integration Points

The file depends on Samba LDAP controls (`server_sort`, `vlv`, `paged_results`, `show_deleted`), SamDB, LDB controls/errors, global catalog port `3268`, and command-line options for test size and attribute filtering. It stresses DSDB indexing, sorting collation, binary/numeric conversion, deleted-object search, ANR filter rewriting, referral handling, and cookie management in the LDAP server stack.

## Risks and Edge Cases

Sorting behavior is sensitive to locale, binary NUL handling, syntax-specific comparisons, and server-specific ordering of equivalent values. The test includes options to skip known-problem attributes, and some comments document Windows/Samba behavioral differences. Randomized mutation loops use fixed seeds but still depend on object counts and server timing. Large `--elements` values can make the combinatorial VLV loops expensive.

## Test Signals

Passing signals include correct sorted windows for all before/after/offset combinations, stable cookie-backed views across additions/deletions, expected attribute updates within existing views, deleted-object ordering with `show_deleted`, rejection of changed paged-search parameters, first-page-only referrals, and correct handling of ANR with paged results.
