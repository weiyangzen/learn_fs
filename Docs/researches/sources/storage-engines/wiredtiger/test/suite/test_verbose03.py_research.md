# sources/storage-engines/wiredtiger/test/suite/test_verbose03.py

## Purpose

`test_verbose03.py` verifies JSON encoding for event-handler messages and errors. It ensures generated JSON can be parsed, follows the expected schema, and carries the expected verbose category IDs.

## Important APIs, Types, and Functions

The class defines context manager `expect_event_handler_json`, plus `test_verbose_json_message` and `test_verbose_json_err_message`. It reuses schema/category validators from `test_verbose_base` and imports `wiredtiger` constants.

## Control Flow

The context manager cleans stdout or stderr, opens a connection with `json_output=[message]` or `json_output=[error]`, yields it, reads messages, parses each line as JSON, validates fields/types and categories, then closes and cleans. Tests trigger API/version messages with table operations and a default-category error by beginning a transaction with invalid read timestamp.

## State and Persistence Behavior

Only temporary tables and captured event-handler output are involved. Error output is explicitly read from stderr in the error-message test.

## Dependencies and Integration Points

Depends on JSON event output, verbose category constants, transaction timestamp validation, and stdout/stderr capture in the Python test harness.

## Risks and Edge Cases

The schema is strict for field names and types, so intentional schema changes require test updates. The error path catches the expected exception and validates emitted diagnostics indirectly.

## Test Signals

Signals are successful JSON parsing, schema validation, correct `WT_VERB_API`, `WT_VERB_VERSION`, or `WT_VERB_DEFAULT` category IDs, and clean resource closure.
