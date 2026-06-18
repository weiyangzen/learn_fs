# sources/storage-engines/wiredtiger/test/suite/test_util12.py

## Purpose

`test_util12.py` exercises `wt write` for insert, overwrite, remove, and argument validation paths. It confirms subprocess writes are visible through a WiredTiger cursor and that invalid invocations report expected utility errors.

## Important APIs, Types, and Functions

The `test_util12` class defines table name/config constants and five test methods: `test_write`, `test_write_overwrite`, `test_write_remove`, `test_write_no_keys`, and `test_write_bad_args`. It uses `runWt`, `check_file_contains`, `session.create`, cursors, and `wiredtiger.WT_NOTFOUND`.

## Control Flow

Tests create a string-key/string-value table, run `wt write` with key/value arguments, reopen a cursor, and assert sorted cursor traversal. Negative cases run the utility with `failure=True` and inspect stderr for `usage:`, duplicate-key, or not-found messages.

## State and Persistence Behavior

The utility mutates table contents directly in the WiredTiger home. Overwrite mode replaces an existing value only with `-o`; remove mode deletes one key only with `-r`.

## Dependencies and Integration Points

Depends on `suite_subprocess` for process execution and on the command implementation for `write`, cursor insertion semantics, duplicate-key handling, and removal semantics.

## Risks and Edge Cases

The test is sensitive to cursor ordering and exact diagnostic wording. It covers string formats only and does not exercise binary/record-number key formats.

## Test Signals

Expected signals are final cursor contents, `WT_NOTFOUND` at end of scan, duplicate-key rejection without `-o`, not-found rejection for remove, and usage output for malformed argument counts.
