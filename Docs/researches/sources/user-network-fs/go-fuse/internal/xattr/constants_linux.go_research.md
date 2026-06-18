<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/constants_linux.go -->
# sources/user-network-fs/go-fuse/internal/xattr/constants_linux.go

## Purpose
Provides the Linux spelling of the missing-xattr error for go-fuse's internal xattr helpers.

## Important APIs, Types, and Functions
Exports `ENOATTR` as `unix.ENODATA`, matching Linux's `getxattr` missing-attribute errno.

## Control Flow
No control flow beyond build-tag selection. Linux builds compile this file instead of the non-Linux constant file.

## State and Persistence Behavior
Stateless constant only; no persistence.

## Dependencies and Integration Points
Used by `posixtest.XAttr` and any FUSE code comparing missing extended attributes portably; depends on `golang.org/x/sys/unix`.

## Risks and Edge Cases
Incorrect errno mapping would make xattr tests fail or hide missing attributes as generic errors.

## Test Signals
Linux xattr tests should call `Getxattr` before and after `Setxattr`/`Removexattr` and compare against `xattr.ENOATTR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/constants_linux.go -->
