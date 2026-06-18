# sources/security-integrity/gocryptfs/tests/root_test/issue893_test.go

## Purpose
Regression tests for issue 893, where credential-changing syscalls began affecting the whole Go process and broke concurrent `allow_other` operations.

## Important APIs, Types, And Functions
- `TestConcurrentUserOps` runs multiple goroutines that switch credentials with `asUser` and perform mkdir/write/unlink cycles.
- `TestAsUserSleep` verifies `asUser` keeps the expected euid stable during concurrent sleeps.

## Control Flow
Both tests skip unless running as root. They spawn goroutines that call the shared thread-locked credential helper and perform either filesystem mutations through the root test mount or direct euid checks.

## State And Persistence
State is temporary directory/file content under `DefaultPlainDir` plus process credential changes confined by `runtime.LockOSThread` in `asUser`.

## Dependencies And Integration Points
Depends on root, the root test package mount, `asUser` from `root_test.go`, and Linux credential behavior.

## Risks And Edge Cases
These tests are concurrency-sensitive and can expose process-wide credential leakage. Failures may leave created directories but the root harness resets temp state between package runs.

## Test Signals
Signals are no credential mismatch and no filesystem operation errors across all concurrent user contexts.
