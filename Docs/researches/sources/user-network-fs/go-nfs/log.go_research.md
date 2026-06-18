<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/log.go -->
# sources/user-network-fs/go-nfs/log.go

## Purpose
Implements the package-level logging abstraction and default logger for go-nfs.

## Important APIs, Types, and Functions
`Logger`, `DefaultLogger`, log levels, `SetLogger`, `ParseLevel`, level getters/setters, and per-level print/printf methods are central.

## Control Flow
Package init reads `LOG_LEVEL`; methods compare configured level against message severity and delegate to the standard `log` package with prefixes.

## State and Persistence Behavior
Global mutable state is `nfs.Log`; default logger stores a level. There is no synchronization around logger replacement or level mutation.

## Dependencies and Integration Points
Used throughout connection and handler code for diagnostics.

## Risks and Edge Cases
`Panic`/`Fatal` methods only log, they do not call `panic` or `os.Exit`, which may surprise callers. Level comparison allows messages at or below the configured threshold per enum ordering.

## Test Signals
Tests should parse all levels, verify filtering, and document non-exiting fatal/panic behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/log.go -->
