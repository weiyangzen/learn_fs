# sources/sync-backup/restic/internal/ui/termstatus/status_test.go

Purpose: validates interactive and noninteractive terminal status behavior.

Important APIs/types/functions: `setupStatusTest()` injects POSIX terminal control functions into a test terminal. Tests cover `SetStatus`, unchanged-line optimization, `Print`, `sanitizeLines`, `readPassword`, raw input/output, disabled status, and `OutputWriter`.

Control flow: tests start `term.Run(ctx)` in a goroutine, send status/messages, cancel, wait for `term.closed`, and assert the exact control-code transcript.

State and persistence: in-memory buffers only. The tests exercise goroutine shutdown and channel flushing through cancellation.

Dependencies/integration: uses `internal/terminal` constants/functions and restic test helpers. `TestOutputWriter` covers integration with `stdio_wrapper.go`.

Risks: exact terminal escape output is brittle but valuable. Some real TTY paths are simulated rather than using an actual terminal.

Test signals: strong regression coverage for status clearing, multi-line status, avoiding redundant redraws, newline normalization, terminal capability disabling, and partial output flushing.
