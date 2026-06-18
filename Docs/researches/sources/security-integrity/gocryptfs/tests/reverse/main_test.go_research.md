# sources/security-integrity/gocryptfs/tests/reverse/main_test.go

## Purpose
Defines the reverse-mode package test harness. It runs the reverse tests across encrypted names, plaintextnames, and deterministic-names modes using a reverse mount plus a forward mount.

## Important APIs, Types, And Functions
- `x240` is a long-name suffix shared by reverse tests.
- `plaintextnames`, `deterministic_names`, `dirA`, `dirB`, and `dirC` are package globals.
- `TestMain` loops over mode combinations and controls mount lifecycle.
- `newReverseFS` initializes and mounts a reverse filesystem, returning backing, mount, and control-socket paths.

## Control Flow
`TestMain` creates `dirA` backing via `newReverseFS`, mounts the encrypted reverse view `dirB` forward at `dirC`, runs all tests, unmounts both layers, cleans temp dirs, and exits on the first failing mode.

## State And Persistence
The harness persists mode globals for each `m.Run` and removes all dirs after each mode. `newReverseFS` creates a config using `InitFS` with reverse-related flags.

## Dependencies And Integration Points
Depends on `test_helpers.InitFS`, `MountOrExit`, `UnmountPanic`, Go test flag parsing, and the gocryptfs binary.

## Risks And Edge Cases
Global state means tests must not assume a single mode. Cleanup depends on successful unmount of both reverse and forward layers.

## Test Signals
Signals are complete success across all three mode rows with clean mount setup and teardown.
