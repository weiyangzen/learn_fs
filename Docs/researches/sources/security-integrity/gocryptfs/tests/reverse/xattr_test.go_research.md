# sources/security-integrity/gocryptfs/tests/reverse/xattr_test.go

## Purpose
Checks xattr pass-through behavior in reverse mode, including list/get on source-created attributes and mountpoint error handling.

## Important APIs, Types, And Functions
- `xattrSupported` probes whether a path supports user xattrs.
- `TestXattrList` creates many `user.*` attrs on a source file and compares the reverse-forward view.
- `TestXattrGetMountpoint` ensures querying the reverse mountpoint does not return `EINVAL`.

## Control Flow
The list test writes xattrs on `dirA`, lists and reads them through `dirC`, filters unrelated `security.*` attributes, and compares names and values. The mountpoint test probes `dirB` directly.

## State And Persistence
State consists of a temporary file and its xattrs in the reverse test backing dir.

## Dependencies And Integration Points
Depends on `github.com/pkg/xattr`, reverse package dirs, and Linux-like xattr semantics.

## Risks And Edge Cases
Xattr support is filesystem-dependent and may skip. Security attributes can appear externally and are ignored to avoid false failures.

## Test Signals
Signals include equal user xattr counts and values through reverse/forward layers, and no `EINVAL` on mountpoint xattr get.
