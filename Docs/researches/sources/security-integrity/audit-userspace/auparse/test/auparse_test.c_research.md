<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/auparse_test.c

Purpose: canonical C integration test for libauparse iteration, searching, feed mode, file and buffer sources, interpretation, record/field cursor movement, and long-event handling.

Important APIs and functions: `walk_test` prints every event, record, field, timestamp, line number, and filename, optionally via `auparse_interpret_field`; `light_test` prints record summaries; `simple_search`, `compound_search`, and `regex_search` exercise `ausearch_add_item`, `ausearch_add_regex`, `ausearch_set_stop`, and `ausearch_next_event`; `auparse_callback` mirrors `walk_test` for feed callbacks. `main` drives `AUSOURCE_BUFFER_ARRAY`, `AUSOURCE_BUFFER`, `AUSOURCE_FILE`, `AUSOURCE_FILE_ARRAY`, and `AUSOURCE_FEED`.

Control flow and state: the static `buf` contains two synthetic audit events; `walked_fields` is reset for `test4.log` and compared with `FIELDS_EXPECTED` to catch parser truncation. Feed tests chunk buffers into three-byte pieces and files into four-byte pieces, then flush to force pending events through callbacks.

Dependencies and integration: uses `libaudit.h`, `auparse.h`, locale setup, and fixture files `test.log`, `test2.log`, and `test4.log`. `run_auparse_tests.sh.in` diffs its stdout against `auparse_test.ref`.

Risks and test signals: output is intentionally brittle and therefore strong at detecting behavior drift, but sensitive to formatting, interpretation table changes, locale, and fixture updates. Failure may be a nonzero exit, a diagnostic in stdout, or a later reference diff mismatch.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_test.c -->
