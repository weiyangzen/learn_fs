
# sources/user-network-fs/rclone/fstest/run.go

Purpose: package `fstest`'s `run.go` provides reusable integration-test setup and teardown for tests that need paired local and remote rclone filesystems.

Important APIs/types/functions: `Run` holds `LocalName`, `Flocal`, `Fremote`, `FremoteName`, precision, cleanup hooks, mkdir cache, and logging callbacks. `TestMain`, `ResetRun`, `NewRun`, `NewRunIndividual`, `Retry`, `WriteFile`, `WriteObjectTo`, `WriteObject`, `WriteUncheckedObject`, `WriteBoth`, listing/check helpers, `CheckDirectoryModTimes`, and `Finalise` are the main APIs.

Control flow: `TestMain` parses flags and either creates one shared run or leaves individual tests to call `NewRunIndividual`. `newRun` initializes fstest, creates a random remote plus a local temp Fs, and computes modify-window precision. Shared-run tests override cleanup to remove all remote entries between tests. Write helpers ensure remote mkdir, compute hashes, retry retriable upload errors, and create matching `Item` records.

State/persistence: uses global `oneRun`, command-line flags, local temp directories, remote random directories, and rclone cache state. Cleanup removes local temp paths, clears cache, and either purges per-test remotes or empties the shared remote.

Dependencies/integration: integrates with `fs`, `cache`, `fserrors`, `hash`, `object`, `walk`, `lib/file`, and `testify`. It is a foundational helper for rclone integration tests outside the generic `fstests.Run` harness.

Risks: shared mode requires robust cleanup; interrupted runs can leave remote data. `Finalise` assumes `cleanRemote` is valid, so partially constructed runs need care. `Retry` only handles caller-provided errors and cannot make non-idempotent writes safe by itself.

Test signals: this file supports tests rather than containing assertions. Its behavior is exercised across rclone integration suites that call `fstest.NewRun`.
