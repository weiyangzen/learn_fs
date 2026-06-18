# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_job_log_parser.go

## Purpose

Parses JSON gcsfuse job download logs for read-cache tests and exposes a helper that returns structured job log entries from a log file.

## Important APIs, control flow, and dependencies

`parseJobLogsFromLogFile` loads lines and delegates each JSON line to `filterAndParseJobLogLine`. The filter unmarshals JSON, extracts timestamp and message, normalizes whitespace with a regexp, and dispatches to `parseJobFileLog` for `downloaded till` messages or `parseChunkDownloadLog` for sparse-file range downloads. `GetJobLogsSortedByTimestamp` opens a log file, parses it, and converts the resulting map to a slice.

## State, persistence, dependencies, and integration points

The parser reads log files from disk but maintains only in-memory maps. Despite the function name, `GetJobLogsSortedByTimestamp` does not sort; it iterates over a map, so ordering is nondeterministic. It depends on shared helper structs and setup log path reporting.

## Risks and test signals

Risks include panic on JSON logs missing timestamp or message, nondeterministic output order, and regex limitations for bucket/object names. Signals are successful parsing of repeated job entries and chunk download ranges in the companion unit tests.
