# sources/test-tools/syzkaller/pkg/vminfo/openbsd.go

## Purpose

`openbsd.go` provides OpenBSD-specific syscall support checks on top of the default no-op checker.

## Important APIs, Types, And Functions

`openbsd` embeds `nopChecker`. Its `syscallCheck` special-cases `openat` through `supportedOpenat` and treats all other calls as supported.

## Control Flow, State, Dependencies, And Integration

The implementation is selected by `New` for OpenBSD targets. It relies on `checkContext` for any `openat` trial execution needed by descriptions with absolute path constants.

## Risks And Test Signals

The narrow implementation can leave unsupported OpenBSD-specific pseudo-devices enabled if not described through `openat`. Generic `TestSyscalls` covers the no-disable path under synthetic success but not real VM behavior.
