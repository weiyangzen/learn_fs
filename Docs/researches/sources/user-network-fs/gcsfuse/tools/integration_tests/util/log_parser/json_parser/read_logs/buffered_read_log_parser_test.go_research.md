# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/buffered_read_log_parser_test.go

## Purpose

Unit-tests the buffered read JSON log parser for successful parsing, ignored noise, fallback detection, restart detection, and key malformed-order errors.

## Important APIs, control flow, and dependencies

`TestParseBufferedReadLogsFromLogReaderSuccessful` builds in-memory log streams with `bytes.NewReader` and expected `map[int64]*read_logs.BufferedReadLogEntry` values. Cases cover one chunk, multiple chunks on the same handle, no fallback, no parsable logs, fallback with random seek count, generic fallback, non-JSON logs, and restart. `TestBufferedReadLogsFromLogReaderUnsuccessful` asserts errors for missing `ReadFile`, response without request, invalid read-file fields, and fallback for unknown handle.

## State, persistence, dependencies, and integration points

The tests are pure unit tests and call `setup.IgnoreTestIfIntegrationTestFlagIsSet` to avoid running during integration-only invocations. They validate parser state transitions across multiple JSON lines and request-ID reverse mapping.

## Risks and test signals

Risks include equality fragility when parser structs gain fields, hard-coded log formats drifting from gcsfuse trace output, and incomplete malformed JSON coverage for panics. Signals are exact struct equality for successful cases and substring matching for expected parser errors.
