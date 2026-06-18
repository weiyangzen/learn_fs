# sources/object-store/minio-mc/cmd/sql-main_test.go

## Purpose
Tests parsing of SQL command serialization option strings.

## Important APIs, types, and functions
- `testParseKVArgsCases` and `TestParseKVArgs` validate raw `key=value` parsing.
- `testParseSerializationCases` and `TestParseSerializationOpts` validate accepted keys, abbreviations, duplicate detection, case normalization, and error messages.

## Control flow
Each table-driven test calls the parser, converts `probe.Error` to a Go error, compares the actual error with an expected full or partial string, and checks expected parsed keys/values are present.

## State and persistence
No state or external dependencies.

## Dependencies and integration points
Targets helper functions from `sql-main.go`; uses standard Go `testing` and `strings`.

## Risks and edge cases
- Tests assert error text fragments, which can be brittle across wording changes.
- They do not check exact map size, so extra parsed keys could go unnoticed in some cases.
- They do not exercise command-level option conflict validation.

## Test signals
Good parser-level regression coverage for common CLI serialization strings and malformed inputs.
