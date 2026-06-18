# sources/user-network-fs/samba/source4/auth/tests/sam.c

Purpose: cmocka unit tests for `source4/auth/sam.c`, especially logon accounting, bad-password persistence, transaction behavior, and memory ownership.

Important APIs/helpers: the test directly includes `auth/sam.c`, wraps `dsdb_search_dn` and `samdb_msg_add_int64`, and mocks LDB transactions, LDB modification requests, DSDB bad-password updates, RODC detection, `ldb_get_opaque`, clustered dbwrap open/store/exists/delete, and message allocation. Helpers build user/domain/PSO results, add binary objectSIDs, and compare extended DNs.

Control flow: reread tests cover search failure, missing computed account-control, locked accounts, and successful rereads. Bad-password update tests cover domain/PSO lookup, transaction start/cancel/commit failures, locked-out rereads, DSDB update failures, no-op updates, LDB request/control/wait failures, and indicator storage. Success-accounting tests cover RODC detection, transaction retry after deciding a write is needed, lastLogonTimestamp failures, request failures, commit/rollback failures, and a spurious bad-password indicator.

State/dependencies/integration: all SAMDB and dbwrap state is mocked. Tests assert transaction booleans and compare `talloc_total_size()` before/after to catch leaks. Linked with wrap ldflags from `wscript_build`.

Risks/test signals: covers account lockout races, audit-noise avoidance, objectSID-keyed temporary indicators, RODC local controls, error mapping, transaction leaks, and memory leaks. Selftest binary `test_auth_sam`.
