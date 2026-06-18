
# sources/sync-backup/kopia/tests/recovery/recovery_test/main_test.go

## Purpose
Defines recovery test process setup, build constraints, shared repo-path constants, and `KOPIA_EXE` gating.

## Important APIs, Types, And Functions
- Build tag restricts tests to Darwin or Linux amd64.
- Constants `dataSubPath`, `dirPath`, and `dataPath` define repository subpaths.
- `repoPathPrefix` flag allows placing recovery repositories under a caller-provided prefix.
- `TestMain` initializes a `kopiaRecoveryTestHarness` and then runs tests.
- `kopiaRecoveryTestHarness.init` exits successfully when `KOPIA_EXE` is absent.

## Control Flow
Before tests run, `TestMain` builds the default data repo path and checks for `KOPIA_EXE`. If missing, it logs and exits with status 0, effectively skipping the package.

## State And Persistence Behavior
No direct repository mutation beyond path selection and harness state.

## Dependencies And Integration Points
Uses `flag`, `os`, and package-level recovery tests that rely on external Kopia binary execution.

## Risks And Edge Cases
Exiting 0 from `TestMain` can hide accidental misconfiguration if a caller expected recovery tests to run. Path constants are shared assumptions for tests in `recovery_test.go`.

## Test Signals
Provides environment gating for binary-dependent recovery tests.
