# sources/user-network-fs/rclone/backend/sftp/ssh_external_test.go

Purpose: regression tests for external SSH process lifecycle behavior.

Important APIs/types/functions: `TestSSHExternalWaitMultipleCalls` creates an external session using `echo test`, starts a quick command, and calls `Wait` three times. `TestSSHExternalCloseMultipleCalls` uses `sleep 10`, starts a long command, closes it, then calls `Wait` repeatedly.

Control flow: both tests instantiate a minimal `Fs` with only `Options.SSH`, call `newSSHSessionExternal`, and assert no panic or inconsistent wait behavior. The close test skips if the local `sleep` command cannot start.

State and persistence behavior: no persistent state. The tests validate that `waitOnce` caches the process wait result and that `exited()` reflects process completion.

Dependencies/integration: uses local system commands (`echo`, `sleep`), rclone `fs.SpaceSepList`, and `testify/assert`. Build tag `!plan9`.

Risks/test signals: targeted coverage for zombie-process/double-wait regressions. It does not test real SSH, subsystem mode, command quoting, or external SFTP data transfer.
