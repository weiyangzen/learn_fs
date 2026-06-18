# sources/storage-engines/pebble/internal/bytesprofile/bytesprofile.go

Purpose: Records byte-count samples grouped by call stack and produces sorted text or structured reports.

APIs and types: `Profile`, `NewProfile`, `Record`, `String`, `Collect`, `StackStats`, and internal `stack`/`aggSamples`.

Control flow and state: `Record` captures callers, locks a mutex, increments count and bytes for the stack. `all` snapshots/sorts stack keys by descending bytes while locked and yields samples. `String` and `Collect` symbolize stack frames with `runtime.CallersFrames`.

Persistence and dependencies: In-memory profiling only. Depends on runtime stack APIs, maps/slices/iter, synchronization, and humanize formatting.

Integration points: Useful for internal allocation/bytes diagnostics where pprof-style export is not yet implemented.

Risks: Holding the mutex while sorting and yielding could block concurrent recorders during formatting. Fixed stack depth of 30 may truncate deep stacks. TODO notes possible pprof export.

Test signals: `bytesprofile_test.go` verifies aggregation, sorting, string output, and structured collection.
