# sources/security-integrity/gocryptfs/tests/root_test/main_test.go

## Purpose
Linux-only root test harness that mounts a default gocryptfs filesystem with `-allow_other` for tests that need uid/gid switching, ACLs, overlay, disk-full, and root-specific behavior.

## Important APIs, Types, And Functions
- `TestMain` resets temp dirs, opens cipherdir permissions, mounts with `-zerokey -allow_other`, runs package tests, unmounts, and removes the temp tree.

## Control Flow
The harness creates a diriv-enabled cipherdir, chmods it to 0777 so switched users can access it, mounts gocryptfs, delegates to `m.Run`, and tears everything down.

## State And Persistence
It owns package-wide temp state in `test_helpers.DefaultCipherDir`, `DefaultPlainDir`, and `TmpDir`.

## Dependencies And Integration Points
Depends on Linux build tag, `test_helpers.ResetTmpDir`, `MountOrExit`, and `UnmountPanic`.

## Risks And Edge Cases
If mount setup fails the whole root package exits. Root and FUSE `allow_other` configuration are prerequisites for useful coverage.

## Test Signals
Success means all root package tests can share one mounted filesystem and cleanup removes the temp tree.
