<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting_other.go -->
# sources/user-network-fs/rclone/fs/accounting/accounting_other.go

## Purpose

`accounting_other.go` supplies the non-Unix implementation of token-bucket signal handling.

## Important APIs, Types, and Functions

It defines `(*tokenBucket).startSignalHandler` as a no-op for builds that are not Darwin, DragonFly, FreeBSD, Linux, NetBSD, OpenBSD, or Solaris.

## Control Flow

When `StartTokenBucket` calls `startSignalHandler` on non-Unix builds, no goroutine or signal registration is created.

## State and Persistence Behavior

No state is mutated. Runtime bandwidth controls remain available through config and rc APIs, but SIGUSR2 toggling is unavailable.

## Dependencies and Integration Points

It is selected by Go build tags and pairs with `accounting_unix.go`.

## Risks and Test Signals

Risks are low but build-tag coverage matters. Cross-compilation should confirm exactly one signal-handler implementation is selected per target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting_other.go -->
