# sources/sync-backup/restic/internal/ui/termstatus/stdio_wrapper.go

Purpose: provides a concurrency-safe line-buffering writer used by `terminal.OutputWriter()`.

Important APIs/types/functions: `lineWriter` contains a mutex, bytes buffer, and `print func(string)`. `newLineWriter()`, `Write()`, and `Close()` implement `io.WriteCloser`.

Control flow: `Write()` appends bytes, finds the last newline, prints all complete lines through the terminal print function, and retains any suffix. `Close()` emits a trailing newline for any remaining partial line.

State and persistence: buffered partial line is in memory and protected by `sync.Mutex`; no persistence.

Dependencies/integration: used by `status.go` so concurrent raw-ish writes are serialized through terminal `Print`, preserving status-line behavior.

Risks: `Close()` does not mark the writer closed, so later writes are still accepted. The callback must itself be safe for the expected call pattern.

Test signals: `stdio_wrapper_test.go` verifies chunked line assembly and race-oriented concurrent writes.
