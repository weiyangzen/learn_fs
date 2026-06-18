<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test_darwin.go -->
# sources/user-network-fs/go-fuse/posixtest/test_darwin.go

## Purpose
Provides Darwin's `F_OFD_GETLK` command number for the POSIX flock test helper.

## Important APIs, Types, and Functions
`sysFcntlFlockGetOFDLock` calls `syscall.FcntlFlock` with constant `92`.

## Control Flow
The shared lock test passes an fd and lock struct; this wrapper performs the platform-specific query.

## State and Persistence Behavior
Stateless helper.

## Dependencies and Integration Points
Used by `FcntlFlockSetLk` on macOS builds.

## Risks and Edge Cases
The hardcoded command value assumes macOS Sierra-or-newer behavior and may not apply to all Darwin-like environments.

## Test Signals
Darwin POSIX test runs validate OFD lock reporting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test_darwin.go -->
