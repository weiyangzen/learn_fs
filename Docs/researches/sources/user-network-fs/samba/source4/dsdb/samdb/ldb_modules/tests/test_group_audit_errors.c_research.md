# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_group_audit_errors.c

Purpose: This companion file validates error handling for group audit JSON construction in `group_audit.c`. It injects failures in JSON infrastructure and checks that `audit_group_json` returns invalid JSON for each failed construction step.

Important APIs, types, and functions: The file directly includes `../group_audit.c`, wraps `json_new_object`, `json_add_version`, and `json_add_timestamp`, and targets `audit_group_json`. Helpers build session data and transaction controls using `auth_session_info`, `security_token`, `dom_sid`, `GUID`, and `DSDB_CONTROL_TRANSACTION_IDENTIFIER_OID`.

Control flow: The test constructs an LDB context/module/request with remote address, session SID/GUID, and transaction GUID. It then forces failures at top-level JSON object creation, version insertion, wrapper creation, and timestamp insertion, asserting `json_is_invalid` each time. A final mock sequence allows all helpers to succeed and asserts the returned object is valid.

State and persistence behavior: All state is transient in talloc allocations and cmocka mock queues. No LDB database or messaging state is created.

Dependencies and integration points: The file depends on cmocka's wrapper/mock mechanism, Samba JSON helpers, LDB request controls, GUID/SID conversion, and group audit internals. It complements `test_group_audit.c` by covering allocation/helper failure paths that are difficult to trigger naturally.

Risks: The exact `will_return` ordering is coupled to implementation allocation order. The file only tests `audit_group_json`; failures in later send paths, membership diffing, or human-readable formatting are outside its scope.

Test signals: Passing tests show group audit JSON construction fails closed under basic JSON helper failures and remains valid on the normal path with the same contextual request data.
