# sources/storage-engines/wiredtiger/test/suite/test_verbose01.py

## Purpose

`test_verbose01.py` defines shared verbose-test helpers and validates legacy verbose configuration without explicit verbosity levels. It covers flat and JSON output formats.

## Important APIs, Types, and Functions

`test_verbose_base` provides `expected_json_schema`, `validate_json_schema`, `validate_json_category`, `create_verbose_configuration`, and context manager `expect_verbose`. `test_verbose01` tests single category, multiple categories, no category, and invalid category behavior.

## Control Flow

`expect_verbose` cleans stdout, opens a new connection with `verbose=[...]` and optional `json_output=[message]`, yields it for operations, reads captured output, optionally parses JSON, matches category patterns, closes the connection, and cleans stdout again.

## State and Persistence Behavior

Tests create short-lived tables and cursors only to trigger verbose messages. Captured stdout is the principal state under inspection.

## Dependencies and Integration Points

Depends on `suite_subprocess`, `wttest` stdout capture, verbose categories such as `api`, `compact`, and `version`, and JSON event-handler formatting.

## Risks and Edge Cases

Output truncation is guarded by dropping the last line when the read cap is reached. Pattern matching validates category strings but not every field in flat messages.

## Test Signals

Signals are generated verbose output only for enabled categories, no output for empty verbose config, JSON schema compliance when requested, and a config error for an unknown category.
