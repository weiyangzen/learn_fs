# sources/sync-backup/restic/cmd/restic/cleanup.go

Purpose: central signal and process-exit helpers for the restic CLI.

Important APIs/functions: `createGlobalContext(stderr)` returns a cancellable root context and registers a goroutine for SIGINT/SIGTERM. `cleanupHandler` logs and prints the signal, optionally dumps stack traces when `RESTIC_DEBUG_STACKTRACE_SIGINT` is set, then cancels the context. `Exit(code)` logs and calls `os.Exit`.

Control flow/state: the signal channel receives one signal and cancels the global context used by commands. Stack traces are written to stderr only on explicit debug environment configuration.

Dependencies/integration: uses Go `os/signal`, `syscall`, and restic `internal/debug`. Command implementations observe context cancellation during repository walks, backup, check, copy, find, and diff operations.

Risks/test signals: only one signal is consumed by the handler; repeated signals follow normal process behavior only if elsewhere configured. The goroutine lives for process lifetime. CI's minimal test sets `RESTIC_DEBUG_STACKTRACE_SIGINT`, but direct signal behavior is usually integration/manual tested.
