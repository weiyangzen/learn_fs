# sources/security-integrity/gocryptfs/tests/root_test/btrfs_test.go

## Purpose
Root-only tests for detecting btrfs fallocate quirks and ensuring the NOCOW attribute suppresses the broken-fallocate quirk.

## Important APIs, Types, And Functions
- `createBtrfsImage` creates, formats, mounts, and returns cleanup for a loop-backed btrfs image.
- `TestBtrfsQuirks` expects `DetectQuirks` to report `QuirkBtrfsBrokenFalloc` on normal btrfs.
- `TestBtrfsQuirksNoCow` applies `chattr +C` and expects that quirk to be absent.

## Control Flow
The helper skips unless root and `mkfs.btrfs` are available, then uses an image file as a mounted btrfs filesystem. Tests run quirk detection on the mount root and on a NOCOW subdirectory.

## State And Persistence
Creates a 200 MiB image and a mounted loop filesystem under `test_helpers.TmpDir`, cleaned by unmount and unlink.

## Dependencies And Integration Points
Depends on root, `mkfs.btrfs`, `mount`, optional `chattr`, and `internal/syscallcompat.DetectQuirks`.

## Risks And Edge Cases
Cleanup does not remove the mount directory and uses plain `syscall.Unmount`; abrupt failures can leave loop mounts. The test is sensitive to kernel btrfs behavior.

## Test Signals
Pass signals are exact quirk detection for normal btrfs and absence of `QuirkBtrfsBrokenFalloc` on NOCOW directories.
