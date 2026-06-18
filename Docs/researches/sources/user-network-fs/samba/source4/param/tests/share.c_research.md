# sources/user-network-fs/samba/source4/param/tests/share.c

Purpose: `param/tests/share.c` defines local torture tests for the generic share API using the classic backend fixture.

Important APIs, types, and functions: Tests include `test_list_empty`, `test_create`, `test_create_invalid`, `test_share_remove_invalid`, `test_share_remove`, `test_double_create`, fixture functions `setup_classic` and `teardown`, and suite factory `torture_local_share`.

Control flow: The suite calls `share_init`, creates a `classic` test case, and obtains a share context from the torture loadparm context. Mutation tests call `share_create`/`share_remove`; if the backend returns `NT_STATUS_NOT_IMPLEMENTED`, the test is skipped. Otherwise they assert creation, invalid parameter, collision, and removal behavior.

State and persistence behavior: For the classic backend, no share mutations persist because create/remove are unsupported and skipped. The fixture context is talloc-freed on teardown.

Dependencies and integration points: It depends on the torture framework, generic share APIs, and loadparm-backed classic context setup.

Risks: Because classic skips mutation tests, the suite does not currently validate a writable backend unless one is added. `test_list_empty` does not assert count, only successful listing.

Test signals: This suite verifies that the share subsystem initializes and that unsupported operations are reported consistently. Writable backend work should extend these tests to avoid skip-only coverage.
