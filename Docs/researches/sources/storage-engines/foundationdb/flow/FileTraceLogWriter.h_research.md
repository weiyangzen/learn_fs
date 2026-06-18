# sources/storage-engines/foundationdb/flow/FileTraceLogWriter.h

## Purpose
Declares the file trace writer and issue reporter types used by Flow tracing.

## Important APIs, Types, And Functions
`IssuesList` implements `ITraceLogIssuesReporter` with `addIssue()`, `retrieveIssues()`, and `resolveIssue()`, plus thread-safe reference counting. `FileTraceLogWriter` implements `ITraceLogWriter` with public `write()`, `open()`, `close()`, `roll()`, `sync()`, `cleanupTraceFiles()`, `lastError()`, and refcount methods.

## Control Flow
The header defines ownership and interface shape; implementation control flow lives in `FileTraceLogWriter.cpp`.

## State And Persistence Behavior
`FileTraceLogWriter` instances carry directory/process/basename/extension/partial-suffix strings, max log size, fd, rolling index, issue reporter reference, and error callback. `IssuesList` hides its synchronized set in `IssuesListImpl`.

## Dependencies And Integration Points
Depends on `Arena`, `FastRef`, and `Trace`. It is consumed by trace-file setup/rotation paths and by status surfaces that report trace issues.

## Risks And Edge Cases
The writer is reference counted but not advertised as internally synchronized for write/open/close sequencing. Callers must provide a live `ITraceLogIssuesReporter` and an `onError` callback suitable for unblocking flush waiters.

## Test Signals
Build coverage ensures interface conformance. Runtime trace tests exercise open/write/roll/sync through `ITraceLogWriter`.
