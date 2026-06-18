# sources/security-integrity/gocryptfs/tests/reverse/force_owner_test.go

## Purpose
Checks reverse-mode `-force_owner` ownership rewriting when mounting a real filesystem root through gocryptfs.

## Important APIs, Types, And Functions
- `TestForceOwner` mounts `/` with `-reverse -zerokey -force_owner=1234:1234` and mode-specific name flags.

## Control Flow
The test creates a temporary mountpoint, mounts the system root in reverse mode, lists root entries, then `Lstat`s the mountpoint and each top-level entry to verify uid/gid rewriting.

## State And Persistence
State is a temporary reverse mount. It does not mutate `/`; it only reads metadata through the mount.

## Dependencies And Integration Points
Depends on `test_helpers.MountOrFatal`, `syscall.Lstat`, and reverse globals for plaintext/deterministic name mode.

## Risks And Edge Cases
Running against `/` means host permissions and mount contents affect coverage. The deferred unmount uses `UnmountErr`, so failures are reported but not panic-cleaned.

## Test Signals
Pass signal is every checked path reporting uid and gid 1234.
