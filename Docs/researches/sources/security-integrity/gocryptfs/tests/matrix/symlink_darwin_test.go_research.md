# sources/security-integrity/gocryptfs/tests/matrix/symlink_darwin_test.go

## Purpose
Provides the Darwin-specific symlink-open test for matrix mounts, using macOS `O_SYMLINK` semantics instead of Linux `O_PATH`.

## Important APIs, Types, And Functions
- `TestOpenSymlinkDarwin` creates a dangling symlink, opens it with `unix.O_SYMLINK`, checks `Fstat` size, unlinks the path, and confirms the open fd remains stat-able.

## Control Flow
The test creates a symlink in the mounted plaintext directory, opens the symlink object itself, validates reported size equals target length, unlinks it, and repeats `Fstat` on the still-open descriptor.

## State And Persistence
Only a single temporary symlink and fd are created. The fd is closed with `defer`; the path is removed during the test.

## Dependencies And Integration Points
Depends on `golang.org/x/sys/unix`, `os`, and the matrix default mount provided by `test_helpers.DefaultPlainDir`.

## Risks And Edge Cases
This is platform-specific; it would not compile or behave correctly on Linux because the open flag differs. It also checks a subtle post-unlink descriptor lifetime contract.

## Test Signals
Success means Darwin can open and stat symlink dentries through gocryptfs and preserve fd validity after unlink.
