# sources/test-tools/syzkaller/pkg/vminfo/netbsd.go

## Purpose

`netbsd.go` provides NetBSD-specific syscall support checks on top of the default no-op checker.

## Important APIs, Types, And Functions

`netbsd` embeds `nopChecker`. Its `syscallCheck` handles `openat` through shared `supportedOpenat`, handles USB connect/disconnect pseudo-syscalls by checking root access to `/dev/vhci0`, and treats all other calls as supported.

## Control Flow, State, Dependencies, And Integration

The file integrates through `New` when `cfg.Target.OS` is NetBSD. It uses `checkContext` runtime helpers, so support depends on executor results and VM file/device availability.

## Risks And Test Signals

Coverage is intentionally narrow; unsupported NetBSD-specific resources not modeled here may remain enabled. Generic `TestSyscalls` in `vminfo_test.go` verifies that, under successful synthetic executor results, no NetBSD calls are unexpectedly disabled.
