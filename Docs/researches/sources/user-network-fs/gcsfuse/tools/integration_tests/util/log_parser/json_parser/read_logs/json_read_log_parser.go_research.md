# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_read_log_parser.go

Purpose: parses JSON-formatted gcsfuse read/cache trace logs into structured entries keyed by file handle, and exposes helpers for tests that need logs sorted by read start timestamp.

Important APIs/types/functions: `filterAndParseLogLine`, `ParseReadLogsFromLogFile`, `GetStructuredLogsSortedByTimestamp`, and `ParseJsonLogLineIntoLogEntryStruct`. It depends on helper parsers in the same package for read-file, file-cache request, and file-cache response messages.

Control flow: each input line is JSON-decoded; non-JSON lines are ignored. Timestamp and message fields are extracted with direct type assertions, whitespace is normalized, and message substrings route the line to one of the specialized parsers. File-cache requests populate a reverse operation-id map so later response logs can update the matching chunk.

State/persistence behavior: all state is in memory: a handle-to-read-entry map and operation-id-to-chunk-index map. The package reads from an `io.Reader` or opened log file but does not persist parser output.

Dependencies/integration: integrates with gcsfuse trace log format, `setup.LogFile()` for error context, and Go tests that inspect read-cache behavior.

Risks/test signals: malformed JSON is ignored, but malformed structured JSON with missing or mistyped fields can panic because of unchecked type assertions. Tests cover expected log sequences, ignored non-JSON logs, and parser errors for missing prerequisite log records.
