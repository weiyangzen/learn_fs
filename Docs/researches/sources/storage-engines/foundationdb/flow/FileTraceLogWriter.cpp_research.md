# sources/storage-engines/foundationdb/flow/FileTraceLogWriter.cpp

## Purpose
Implements file-backed TraceEvent log writing, issue tracking, retry-on-error behavior, rolling files, finalizing partial trace files, fsync, and trace-directory cleanup.

## Important APIs, Types, And Functions
`IssuesListImpl` stores current trace issues under a mutex. `IssuesList` implements `ITraceLogIssuesReporter`. `FileTraceLogWriter::write()`, `open()`, `close()`, `roll()`, `sync()`, `cleanupTraceFiles()`, and `lastError()` implement `ITraceLogWriter`. Platform macros map POSIX and Windows open/write/close/fsync calls.

## Control Flow
`open()` cleans old files, increments an index, creates an exclusive filename using basename/index width/index/extension/partial suffix, retries on conflicts or create failures, tracks latest open errors on the main thread, and resolves the issue once successful. `write()` loops until all bytes are written, adding `trace_log_file_write_error` on failures, invoking `onError()` for non-EINTR errors, and sleeping before retry. `close()` closes the descriptor and renames partial files to final names. `cleanupTraceFiles()` finalizes stale partial files, sorts trace files newest-first, and deletes beyond `maxLogsSize`.

## State And Persistence Behavior
Persists trace data to files in `directory`, mutates filenames by rename/delete, and keeps process-local fd/index/finalname/issue state. Cleanup is disabled in simulation and when `maxLogsSize == 0`.

## Dependencies And Integration Points
Depends on `FileTraceLogWriter.h`, platform file helpers, `ThreadHelper.actor.h`, `FLOW_KNOBS` retry/padding values, `g_network`, latest-event cache, and TraceEvent infrastructure.

## Risks And Edge Cases
`write()` treats all non-positive returns as retryable and stores `remaining` in `int`, so extremely large writes rely on upstream chunking. Permanent write failures unblock flush barriers via `onError()` but can spin with sleeps. Filename sorting is lexical by generated names; the index-width component is intended to preserve recency ordering. Cleanup silently ignores `Error`.

## Test Signals
No direct unit test. Signals include trace-file creation/rollover in Flow tests, issue reporter contents, `TraceFileOpenError` latest-event behavior, fsync error stderr, and disk cleanup side effects.
