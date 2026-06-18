# sources/sync-backup/git-lfs/subprocess/subprocess_nix.go

Purpose: non-Windows subprocess constructor.

Important API: `ExecCommand(name string, arg ...string)`.

Control flow: creates `exec.Command`, resolves the executable with package `LookPath`, assigns sanitized cached environment, wraps in `Cmd`, and returns.

State/persistence behavior: no direct persistence; reads environment through `fetchEnvironment`.

Dependencies/integration: all non-Windows command execution in Git LFS uses this path.

Risks: returns early if lookup fails, so callers do not get a partially constructed command. Environment filtering removes trace and super-prefix variables from all child commands.

Test signals: Unix CI and integration tests exercise command discovery/execution.
