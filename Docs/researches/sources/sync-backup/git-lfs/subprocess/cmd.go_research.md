# sources/sync-backup/git-lfs/subprocess/cmd.go

Purpose: wraps `exec.Cmd` to centralize tracing and pipe cleanup.

Important APIs/types/functions: `Cmd`, `Run`, `Start`, `Output`, `CombinedOutput`, `StdoutPipe`, `StderrPipe`, `StdinPipe`, `Wait`, `trace`, and `newCmd`.

Control flow: execution methods trace before delegating to `exec.Cmd`. Pipe factory methods append created pipes to an internal slice. `Wait` closes all recorded pipes before waiting on the child process.

State/persistence behavior: in-memory tracking of pipes associated with a command. Child process side effects are determined by the command.

Dependencies/integration: used by all subprocess spawning in Git LFS, including SSH transfer.

Risks: pipe methods append even if `exec.Cmd` returns an error, which can append nil closers if a future Go version does so. Closing pipes before `Wait` is intentional but can surprise code expecting to read after wait.

Test signals: no direct tests; subprocess behavior and tracing are exercised throughout integration tests.
