# sources/sync-backup/git-lfs/subprocess/subprocess_windows.go

Purpose: Windows subprocess constructor.

Important API: `ExecCommand(name string, arg ...string)`.

Control flow: creates `exec.Command`, resolves executable via package `LookPath`, sets `SysProcAttr.HideWindow = true`, assigns sanitized cached environment, wraps in `Cmd`, and returns.

State/persistence behavior: no persistence; influences child-process window behavior and environment.

Dependencies/integration: all Windows Git LFS subprocess execution goes through this path.

Risks: hidden-window behavior is Windows-specific and important for GUI/no-console use. Command lookup relies on `PATHEXT` handling in `path_windows.go`.

Test signals: Windows CI/integration tests cover executable lookup and hidden child execution behavior indirectly.
