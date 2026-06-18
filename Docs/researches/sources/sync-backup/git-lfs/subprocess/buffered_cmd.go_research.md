# sources/sync-backup/git-lfs/subprocess/buffered_cmd.go

Purpose: defines `BufferedCmd`, a convenience wrapper for subprocesses with buffered stdin/stdout/stderr handles.

Important APIs/types: `stdoutBufSize` constant and `BufferedCmd` struct embedding `*Cmd` with `Stdin`, `Stdout`, and `Stderr` fields.

Control flow: no functions in this file; instances are constructed by `BufferedExec` and `StdoutBufferedExec`.

State/persistence behavior: holds pipe handles and readers for a running subprocess. Persistence is external to the child process.

Dependencies/integration: part of the `subprocess` package used by Git LFS helpers that need interactive child processes.

Risks: consumers must still call `Wait`/close paths through `Cmd` to avoid process and pipe leaks.

Test signals: indirect through callers; no direct unit tests for this struct.
