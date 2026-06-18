# sources/storage-engines/wiredtiger/test/suite/test_util11.py

## Purpose

`test_util11.py` verifies the `wt list` utility against an initially empty database, a database with several tables, dropped-table cases, and the `-f` output-file option. It is a Python suite test built on `wttest.WiredTigerTestCase` and `suite_subprocess` so it can create tables through the API and then inspect `wt` subprocess output.

## Important APIs, Types, and Functions

The test class `test_util11` defines `populate`, `create_tables`, and `compare_two_files` helpers plus test methods for empty listing, normal listing, listing after partial/all drops, and custom file output. It uses `session.create`, `open_cursor`, `dropUntilSuccess`, `runWt`, `check_file_content`, and file comparison.

## Control Flow

Each test constructs table state, runs `wt list` with optional URI prefixes or `-c -f`, and compares stdout or a target file with an expected sorted table URI list.

## State and Persistence Behavior

The persistent state is WiredTiger table metadata and one inserted key/value in selected tables. Drop tests assert list output follows metadata removal. The `-f` case persists output in a named local file.

## Dependencies and Integration Points

Depends on the WiredTiger Python test framework, the `wt` binary wrapper in `suite_subprocess`, and metadata/listing behavior in the utility layer.

## Risks and Edge Cases

The final custom-output comparison currently calls `compare_two_files` without asserting its boolean result, so a regression could be missed unless the helper raises elsewhere. Expected output assumes deterministic list ordering.

## Test Signals

Good signals are exact output matches, empty stdout when custom output is requested, no listed dropped tables, and successful operation with both populated and empty objects.
