# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_audit_log_errors.c

Purpose: This companion cmocka file verifies error handling in `audit_log.c` JSON construction. It deliberately injects failures in JSON object creation, version insertion, and timestamp insertion to ensure audit formatter functions return invalid JSON rather than partially valid events.

Important APIs, types, and functions: The file directly includes `../audit_log.c` and wraps `json_new_object`, `json_add_version`, and `json_add_timestamp` through linker-style cmocka wrappers. It targets `operation_json`, `password_change_json`, `transaction_json`, `commit_failure_json`, and `replicated_update_json`. Test fixtures build `struct ldb_context`, `struct ldb_module`, `struct ldb_request`, `struct ldb_reply`, `struct audit_private`, session/security token data, and replication structures.

Control flow: Each test first constructs enough request context for a happy-path formatter call. It then uses ordered `will_return` values to force a specific allocation or helper failure, calls the formatter, and asserts `json_is_invalid`. After the negative paths, it supplies successful wrapper returns and checks the formatter can still produce valid JSON.

State and persistence behavior: All state is in-memory and scoped to talloc contexts. The wrapper functions use cmocka's mock queue as transient state. The tests do not exercise module transactions or persistent LDB storage.

Dependencies and integration points: The test relies on cmocka wrapping support, Samba's JSON abstraction, LDB private structures, GUID/SID helpers, and DSDB replication types. It integrates with the same implementation functions as `test_audit_log.c` but focuses on failure propagation rather than field-level schema validation.

Risks: The tests are sensitive to the number and order of JSON helper calls in the implementation; harmless refactors that allocate wrappers in a different order can break the mock sequence. Conversely, they cover only selected failure points, so errors after timestamp insertion or while adding later fields may need separate tests.

Test signals: Passing tests show that top-level audit JSON formatters fail closed when basic JSON infrastructure fails and still produce valid JSON on the happy path after mocked failures are cleared.
