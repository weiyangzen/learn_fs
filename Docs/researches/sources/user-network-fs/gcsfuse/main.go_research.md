## sources/user-network-fs/gcsfuse/main.go

Purpose: Entry point for the gcsfuse command-line binary.

Important APIs/types/functions: `logPanic`, `main`, and `go:generate` directives for config and metrics code generation.

Control flow: `main` defers panic recovery through `logPanic`, configures standard log timestamp flags, starts goroutines for CPU and memory profiling signal handlers, then delegates command execution to `cmd.ExecuteMountCmd()`.

State and persistence behavior: process-level logging configuration and profiling signal handlers. Any persistent effects are downstream of mount command execution.

Dependencies and integration points: integrates `cmd`, internal logger, and internal perf signal handlers. Generation directives connect `cfg/params.yaml` and `metrics/metrics.yaml` to generated Go files.

Risks: `logPanic` only catches panics in the main goroutine, not profiling goroutines or workers. Profiling handlers run for process lifetime. Generation comments are operationally important and should not be removed.

Test signals: no direct test in this subset; behavior is typically covered by command/integration tests.
