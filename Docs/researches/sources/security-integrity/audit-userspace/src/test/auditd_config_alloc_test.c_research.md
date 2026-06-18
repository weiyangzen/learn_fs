<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/auditd_config_alloc_test.c -->
# sources/security-integrity/audit-userspace/src/test/auditd_config_alloc_test.c

**Purpose**
This C test injects allocation failures into selected auditd configuration parser paths and verifies that existing configuration values are preserved when replacement allocation fails.

**Important APIs, Types, And Functions**
The test defines stubs for `audit_msg`, `audit_strsplit`, and `time_string_to_seconds`, then macro-replaces `malloc`, `strdup`, and `asprintf` before including `../auditd-config.c`. `reset_allocs`, `should_fail`, `test_malloc`, `test_strdup`, and `test_asprintf` implement deterministic fail-at-N allocation behavior. Test cases call `name_parser`, `log_file_parser`, and `set_config_dir`.

**Control Flow**
`main` disables failures, then runs three checks. `test_name_preserves_old_value` seeds `daemon_conf.node_name`, fails the first allocation, expects parser failure, and asserts the old name remains. `test_log_file_preserves_old_value` sets `log_test = TEST_SEARCH`, fails the second allocation path, and verifies the original log file path. `test_set_config_dir_preserves_old_value` establishes old global paths, forces a failure on replacing the directory, and checks both globals remain unchanged.

**State And Persistence**
The harness mutates in-memory `daemon_conf` fields plus the global `config_dir` and `config_file` from the included implementation. It cleans those globals at the end to avoid leak reports.

**Dependencies And Integration Points**
It depends directly on auditd-config internals and GNU `vasprintf`. The Makefile compiles it with auditd include paths and no external daemon process.

**Risks**
Macro-replacing allocators only covers allocations in the included translation unit after the defines; helper functions outside that inclusion are not exercised. The test relies on exact allocation ordering, so benign refactors can require fail counter updates.

**Test Signals**
Assertions validate regression behavior for allocation failure atomicity: failed parser updates must not partially replace previous config strings.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/auditd_config_alloc_test.c -->
