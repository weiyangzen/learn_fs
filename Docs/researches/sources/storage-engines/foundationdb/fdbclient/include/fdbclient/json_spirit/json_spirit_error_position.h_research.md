<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_error_position.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_error_position.h

## Purpose
`json_spirit_error_position.h` declares the small error-position object thrown by json_spirit parsing functions that report line and column information.

## Important APIs, Types, and Functions
The file defines `json_spirit::Error_position` with default and `(line, column, reason)` constructors, equality, and public fields `line_`, `column_`, and `reason_`.

## Control Flow
Position-aware parser paths construct `Error_position` when invalid input is found. Equality compares reason, line, and column, with a fast self-comparison path.

## State and Persistence Behavior
The type is transient exception/diagnostic state. It has no database persistence and no global state.

## Dependencies and Integration Points
It depends only on `<string>` and is included by `json_spirit_reader_template.h`. Callers catching parse errors can inspect line, column, and reason.

## Risks and Edge Cases
The fields are public and unsigned, so absent positions default to zero. Non-position parser paths may throw strings instead of this type, so callers need to know which API they used.

## Test Signals
Parser tests for invalid JSON through `read_*_or_throw` should assert line, column, and reason values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_error_position.h -->
