<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_extra_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/auparse_extra_test.c

Purpose: focused C regression coverage for auparse behaviors that are narrower than the main text-output harness: buffer replacement, feed state, normalization, timestamp-expression validation, escaped path normalization, single-character empty field parsing, and event-level search matching across multi-record events.

Important APIs and functions: `test_new_buffer` validates `auparse_new_buffer`; `test_feed_state` uses `AUSOURCE_FEED`, `auparse_add_callback`, `auparse_feed_has_data`, `auparse_feed`, and `auparse_flush_feed`; `test_normalize` checks `auparse_normalize`, `auparse_normalize_get_event_kind`, subject/object cursor helpers, and `auparse_interpret_realpath`; `test_compare` checks node and timestamp comparison; `test_timestamp_milli` drives `ausearch_add_expression`; `test_path_norm` calls `audit_encode_value` and `auparse_do_interpretation`; `test_cur_event_matches_multirecord_event` exercises `ausearch_cur_event`.

Control flow and state: `main` runs independent assert-based tests, each creating and destroying its own `auparse_state_t` except for local synthetic `idata`. Feed tests rely on callback count as transient global state. The path fuzz test enumerates base-3 strings over `/`, `a`, and `.` to stress normalization without persistent output.

Dependencies and integration: depends on `libaudit.h`, `auparse.h`, and internal `auparse-idata.h`; uses local `test.log`. It is integrated as an auparse test binary, but broader shell harnesses may choose which binaries to run.

Risks and test signals: risks include assert-only diagnostics, dependence on `root`/audit interpretation tables, and a large path-fuzz print stream. Passing prints `extra auparse tests: all passed`; failures abort at the exact invariant that regressed.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_extra_test.c -->
