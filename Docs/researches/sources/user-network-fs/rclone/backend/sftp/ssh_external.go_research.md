# sources/user-network-fs/rclone/backend/sftp/ssh_external.go

Purpose: implements SFTP's SSH abstraction using an external `ssh` command configured by the `ssh` option.

Important APIs/types/functions: `sshClientExternal` stores the backend and first session; `newSSHClientExternal` creates the client wrapper; `Wait`, `Close`, `NewSession`, and `CanReuse` coordinate the process-backed session. `sshSessionExternal` wraps `exec.Cmd`, cancellation, start state, SFTP-vs-command mode, and `sync.Once`-guarded wait result. `requestSubsystem` is a sentinel prefix translated into `ssh -s <subsystem>`.

Control flow: each session creates a cancellable `exec.CommandContext` from configured args. `Start` appends either `-s subsystem` or a remote command and starts the process. `RequestSubsystem` uses the sentinel path. `Run` starts then waits. `Close` cancels context and waits. `CanReuse` returns true only while the first external session is still running the SFTP subsystem.

State and persistence behavior: process state is in memory. `waitOnce` prevents duplicate waits and associated zombie/process-state hazards. Environment setting is deliberately unsupported and returns an error.

Dependencies/integration: uses `os/exec`, `context`, `slices.Clone`, `sync`, and rclone logging. It plugs into `sftp.go` connection creation and command execution; user must configure passwordless external SSH and keepalives themselves.

Risks/test signals: risks include argument construction, external process lifecycle, inability to set env vars, and different reuse semantics from internal SSH. `ssh_external_test.go` verifies repeated `Wait`/`Close` safety.
