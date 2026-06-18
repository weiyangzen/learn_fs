# sources/sync-backup/restic/internal/ui/termstatus/status.go

Purpose: concrete `ui.Terminal` implementation that serializes normal output, error output, and status-line updates.

Important APIs/types/functions: `Setup()` starts the terminal goroutine and returns a shutdown function; `new()` detects TTY capabilities; methods implement `InputRaw`, `ReadPassword`, `CanUpdateStatus`, `OutputWriter`, `OutputRaw`, `Run`, `Flush`, `Print`, `Error`, `SetStatus`; helpers include `writeStatus`, `runWithoutStatus`, `sanitizeLines`, and `findUnchangedLines`.

Control flow: `Run()` chooses interactive in-place status updates or simple output mode. Interactive mode clears current status before printing messages, redraws status, skips writes while backgrounded, and clears on cancellation. Noninteractive mode prints changed status lines as ordinary lines.

State and persistence: channel-driven goroutine owns terminal state. `lastStatus` tracks redraw diffs; `sync.Once` lazily creates a line-buffering output writer. No persistence.

Dependencies/integration: depends on `internal/terminal` for TTY detection/control codes/password reading and on `ui` formatting helpers.

Risks: channel sends after shutdown are dropped; incorrect terminal width can over-truncate; background-process checks suppress output.

Test signals: tests verify cursor sequences, unchanged-line optimization, sanitization, raw IO, disabled status, password fallback, and `OutputWriter`.
