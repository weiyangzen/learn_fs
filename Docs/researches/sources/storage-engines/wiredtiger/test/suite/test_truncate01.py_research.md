<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate01.py

Purpose: Base and broad API coverage for `session.truncate` over files, tables, simple/complex datasets, cursor ranges, empty objects, timestamp/no-timestamp transactions, and varied key formats.

Important APIs/types/functions: Defines `test_truncate_base` with common connection config and multiple test classes for bad arguments, URI truncation, cursor ordering, cursor past-end ranges, empty objects, timestamp handling, and cursor-range truncation. Uses `SimpleDataSet`, `ComplexDataSet`, `confirm_empty`, `simple_key`, `make_scenarios`, `session.truncate`, and helper `truncateRangeAndCheck`.

Control flow: The file first validates invalid argument combinations and unset cursor keys. It then truncates whole objects by URI, rejects reversed cursor ranges, permits ranges past the end, handles empty objects, and tests no-timestamp truncate under logging. The large cursor-range suite constructs many record layouts with skipped/inserted prefixes and suffixes, optionally checkpoints/reopens, truncates selected ranges, and validates remaining keys.

State and persistence behavior: Tests both in-memory insert-list state and on-disk state after checkpoint/reopen. It also covers logged versus unlogged object timestamp rules and complex table indexes/column groups.

Dependencies and integration points: This is the baseline for later truncate tests; `test_truncate02.py` inherits `test_truncate_base`. It integrates schema, cursor positioning, file/table namespaces, disaggregated hook skips, and transaction synchronization/statistics config.

Risks: Scenario count is high and uses pruning; regressions can be format-specific. The `test_truncate_complex` method appears to run only when `type == 'table:'` and `runningHook('disagg')`, despite comments suggesting broad table smoke coverage, so non-disagg complex table coverage may be intentionally or accidentally skipped.

Test signals: Expected exceptions, `confirm_empty`, `WT_NOTFOUND` for deleted keys, exact retained values, and drop/reopen cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate01.py -->
