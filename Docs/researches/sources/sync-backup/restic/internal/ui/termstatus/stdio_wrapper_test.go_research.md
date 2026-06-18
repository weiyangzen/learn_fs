# sources/sync-backup/restic/internal/ui/termstatus/stdio_wrapper_test.go

Purpose: verifies `lineWriter` buffering and concurrent write safety.

Important APIs/types/functions: `TestStdioWrapper` feeds byte chunks into `newLineWriter`; `TestStdioWrapperConcurrentWrites` uses `errgroup` to write from five goroutines.

Control flow: table cases cover no newline until close, split complete lines, multiple lines in one write, and retained suffix emission on close.

State and persistence: only in-memory `strings.Builder` output. Concurrent test relies on mutex protection and is most useful with `go test -race`.

Dependencies/integration: uses `go-cmp` for diffs and restic test helpers for error assertions.

Risks: concurrent test does not verify line ordering, only absence of returned errors and race safety under race detector.

Test signals: good coverage for complete-line flushing, partial-line retention, close-time newline normalization, and basic thread safety.
