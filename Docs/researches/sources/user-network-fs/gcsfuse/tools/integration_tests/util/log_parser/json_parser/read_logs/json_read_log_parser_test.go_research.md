# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_read_log_parser_test.go

Purpose: unit-tests the JSON read-log parser used by integration tests for read cache and file cache behavior.

Important APIs/types/functions: `TestParseLogFileSuccessful`, `TestParseLogFileUnsuccessful`, shared constants for timestamps, object metadata, handle ids, and `chunkData` expected output. Tests use `ParseReadLogsFromLogFile` and compare maps of `StructuredReadLogEntry`.

Control flow: successful cases feed in-memory multiline log streams covering a single chunk, repeated chunks, irrelevant JSON logs, and non-JSON input. Failure cases omit the preceding read or file-cache request logs or corrupt numeric tokens to ensure parser errors contain expected fragments.

State/persistence behavior: tests are pure in-memory `bytes.Reader` cases and call `setup.IgnoreTestIfIntegrationTestFlagIsSet`, so they are intended for normal unit-test runs rather than integration-test executions.

Dependencies/integration: depends on `testify/assert`, `testify/require`, and exact gcsfuse trace-message shapes.

Risks/test signals: tests validate happy paths and several parser-level errors, but they do not cover JSON records with missing `timestamp` or `message` fields that could panic in production parser code.
