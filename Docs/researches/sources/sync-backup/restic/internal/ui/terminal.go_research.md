# sources/sync-backup/restic/internal/ui/terminal.go

Purpose: defines the common `ui.Terminal` interface used by restic components for output, status, and password input.

Important APIs/types/functions: the interface includes `Print`, `Error`, `SetStatus`, `CanUpdateStatus`, raw input/output accessors, terminal detection, `ReadPassword`, `OutputWriter`, and `OutputRaw`.

Control flow: none in this file; it is a contract. Comments specify newline handling, concurrent-safe output writer behavior, and the restriction that `OutputRaw` must not be mixed with managed terminal methods.

State and persistence: no state.

Dependencies/integration: depends only on `context` and `io`. Implemented by `internal/ui/termstatus.terminal` and likely mocked by tests.

Risks: callers using `OutputRaw` can break status rendering if they ignore the contract. Interface expansion has broad compile-time impact across UI consumers.

Test signals: implementation behavior is tested in `termstatus/status_test.go`; this file itself has no unit tests.
