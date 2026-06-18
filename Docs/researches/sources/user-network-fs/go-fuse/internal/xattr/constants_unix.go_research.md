<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/constants_unix.go -->
# sources/user-network-fs/go-fuse/internal/xattr/constants_unix.go

## Purpose
Provides the non-Linux spelling of the missing-xattr error for portable xattr handling.

## Important APIs, Types, and Functions
Exports `ENOATTR` as `unix.ENOATTR` on non-Linux builds.

## Control Flow
Build tags choose this file outside Linux; there is no runtime branch.

## State and Persistence Behavior
Stateless constant only.

## Dependencies and Integration Points
Used by the common xattr tests and any platform-specific FUSE code needing a portable not-found comparison.

## Risks and Edge Cases
Platform headers vary; unsupported platforms could fail to define `ENOATTR` or map it differently.

## Test Signals
FreeBSD/Darwin xattr tests should verify missing attributes compare equal to this constant.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/constants_unix.go -->
