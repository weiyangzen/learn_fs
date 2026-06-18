# sources/sync-backup/restic/internal/fs/fs_reader_command.go

Purpose: Exposes subprocess stdout as an `io.ReadCloser` suitable for `NewReader`.

Important APIs: `commandReader`, `NewCommandReader`, `Read`, `wait`, and `Close`.

Control flow and state: `NewCommandReader` validates args, sets up stdout/stderr pipes, starts a goroutine that forwards stderr lines to a callback, then starts the command. `Read` reads stdout and, on EOF, waits once for command exit so failures are reported even if output was empty. `Close` cancels unfinished commands and waits.

Dependencies and integration: Uses `exec.CommandContext`, restic errors, and caller-provided error-output logging. Intended for backup from command output.

Risks: The stderr scanner goroutine starts before `Start`; pipe behavior depends on `exec`. `alreadyClosedReadErr` caches terminal errors, so callers see consistent post-close behavior. Fatal command errors abort snapshot flows.

Test signals: `fs_reader_command_test.go` covers success, failure exit status, invalid command, empty args, captured stdout, and quick close of a long-running process.
