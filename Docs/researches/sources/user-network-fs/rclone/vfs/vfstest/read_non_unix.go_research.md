# sources/user-network-fs/rclone/vfs/vfstest/read_non_unix.go

## Purpose
Provides a non-Unix fallback for the read double-close test.

## APIs, Flow, And State
`TestReadFileDoubleClose` skips with the current operating system. No state is created.

## Dependencies And Integration
Selected outside Linux, Darwin, and FreeBSD where the Unix `dup`/close test is not available.

## Risks And Test Signals
The read-after-dup-close behavior is not validated on these platforms. The file ensures test package build consistency and explicit skip reporting.
