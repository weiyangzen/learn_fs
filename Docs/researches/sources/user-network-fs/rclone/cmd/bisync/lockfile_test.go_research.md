# sources/user-network-fs/rclone/cmd/bisync/lockfile_test.go

Purpose: Unit tests for `lockFileIsExpired` behavior around corrupt and time-bounded lock files.

Important APIs/types/functions: `newTestLockfileBisyncRun` creates a temp lock file plus placeholder listing files and returns a minimal `bisyncRun`. Tests are `TestLockfileIsExpired_UnreadableWithMaxLock`, `TestLockfileIsExpired_UnreadableWithoutMaxLock`, `TestLockfileIsExpired_ValidExpired`, and `TestLockfileIsExpired_ValidNotExpired`.

Control flow: Each test writes either invalid JSON or JSON matching lock metadata fields, configures `Options.MaxLock`, calls `lockFileIsExpired`, and asserts the expected boolean. The helper also creates listing files because expired/corrupt-with-max-lock cases call `markFailed`.

State and persistence behavior: Tests use `t.TempDir` and write lock/listing files with `0600`. The function under test may rename listing files to `-err`; the current assertions focus on expiration boolean rather than side effects.

Dependencies and integration points: Uses Go testing, testify assert/require, rclone `fs.Duration`, and the package-private `bisyncRun` internals because it is in package `bisync`.

Risks: The tests do not assert listing rename side effects, close-error paths, max-lock clamping, or renewal behavior. They use wall-clock `time.Now`, but windows are wide enough to avoid flake.

Test signals: These are fast unit-level checks complementing the larger golden integration suite. A regression that treats corrupt locks as expired without max-lock, or fails to expire stale JSON locks, should fail here.
