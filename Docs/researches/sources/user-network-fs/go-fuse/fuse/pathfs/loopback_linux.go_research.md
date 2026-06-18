# `sources/user-network-fs/go-fuse/fuse/pathfs/loopback_linux.go`

## Purpose
Adds Linux xattr and timestamp support for the loopback pathfs implementation.

## Important APIs, Types, And Functions
Exports loopback methods `ListXAttr`, `GetXAttr`, `SetXAttr`, `RemoveXAttr`, `String`, and `Utimens`; `Utimens` builds two `Timespec` values and calls `sysUtimensat` with `_AT_SYMLINK_NOFOLLOW`.

## Control Flow
Exports loopback methods `ListXAttr`, `GetXAttr`, `SetXAttr`, `RemoveXAttr`, `String`, and `Utimens`; `Utimens` builds two `Timespec` values and calls `sysUtimensat` with `_AT_SYMLINK_NOFOLLOW`.

## State And Persistence
State lives in the backing filesystem xattr/timestamp metadata. Dependencies are Linux `syscall` xattr calls and the local xattr/list helpers. Risks include ERANGE retry sizing and Linux-only no-follow timestamp semantics. Covered by pathfs xattr and utimens tests.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State lives in the backing filesystem xattr/timestamp metadata. Dependencies are Linux `syscall` xattr calls and the local xattr/list helpers. Risks include ERANGE retry sizing and Linux-only no-follow timestamp semantics. Covered by pathfs xattr and utimens tests.

## Test Signals
State lives in the backing filesystem xattr/timestamp metadata. Dependencies are Linux `syscall` xattr calls and the local xattr/list helpers. Risks include ERANGE retry sizing and Linux-only no-follow timestamp semantics. Covered by pathfs xattr and utimens tests.
