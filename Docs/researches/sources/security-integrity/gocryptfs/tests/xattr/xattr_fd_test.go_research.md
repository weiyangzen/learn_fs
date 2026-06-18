# sources/security-integrity/gocryptfs/tests/xattr/xattr_fd_test.go

## Purpose
Linux-only tests for file-descriptor xattr syscalls through a gocryptfs mount.

## Important APIs, Types, And Functions
- `TestFdXattr` opens a file, uses `Flistxattr`, `Fsetxattr`, `Fgetxattr`, and `Fremovexattr`, and verifies list sizes and values.

## Control Flow
The test creates a file in the mounted plaintext dir, opens it once, performs fd-based xattr operations, and checks the xattr list before set, after set, and after removal.

## State And Persistence
State is one temporary file and one `user.foo` xattr, removed by test cleanup through temp-dir teardown.

## Dependencies And Integration Points
Depends on Linux fd xattr APIs from `golang.org/x/sys/unix` and the xattr integration package `TestMain` mount.

## Risks And Edge Cases
Darwin is excluded because it lacks these fd APIs. The expected list size includes the NUL terminator from Linux `flistxattr`.

## Test Signals
Pass signals are empty initial/final lists, exact listed name, and exact readback value.
