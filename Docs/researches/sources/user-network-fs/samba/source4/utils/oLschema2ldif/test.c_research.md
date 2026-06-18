<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/test.c -->
# sources/user-network-fs/samba/source4/utils/oLschema2ldif/test.c

## Purpose

This file contains cmocka regression tests for malformed or unsupported OpenLDAP schema inputs handled by the `oLschema2ldif` library.

## Important APIs, Types, and Functions

- `setup_context()` and `teardown_context()` allocate/free a small talloc test context.
- `process_data_blob()` wraps an in-memory input blob with `fmemopen()`, writes output to `/dev/null`, creates an LDB context/base DN, and calls `process_file()`.
- Tests cover unknown syntax OID, unterminated quoted token value, unterminated `MUST`, `MAY`, and `SUP` values, unknown tokens, and missing `NAME`.
- `main()` registers tests with cmocka and emits subunit output.

## Control Flow

Each test constructs one schema definition blob, invokes `process_data_blob()`, then asserts `ret.count == 1` and `ret.failures == 1`. The helper closes the in-memory input and `/dev/null` output after conversion.

## State and Persistence Behavior

No durable state is written. `/dev/null` receives generated LDIF if conversion unexpectedly succeeds. All allocations are under the test talloc context and are freed in teardown.

## Dependencies and Integration Points

The tests depend on cmocka, `fmemopen()`, LDB, Samba talloc/includes, and `oLschema2ldif-lib`. The build enables `test_oLschema2ldif` only when `HAVE_FMEMOPEN` is set.

## Risks and Edge Cases

The tests cover negative parse paths but not successful conversion output. They assert only aggregate counts, so they do not validate diagnostics or partially emitted LDIF content. They rely on `/dev/null`, which is Unix-specific but suitable for Samba's build targets.

## Test Signals

The expected signal is every malformed fixture being counted as one attempted record with one failure. A success count without failure would indicate the parser accepted malformed or unsupported schema input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/test.c -->
