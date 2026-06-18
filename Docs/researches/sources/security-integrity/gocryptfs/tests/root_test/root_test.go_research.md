# sources/security-integrity/gocryptfs/tests/root_test/root_test.go

## Purpose
Contains root-only integration tests for credential switching, supplementary groups, ENOSPC handling, ACL enforcement, overlayfs compatibility, and `-force_owner` operations.

## Important APIs, Types, And Functions
- `asUser` locks the current OS thread, sets groups/gid/uid, runs a callback, and resets real/effective/saved ids and gids.
- `TestSupplementaryGroups` checks group-based access under `allow_other`.
- `writeTillFull` and `TestDiskFull` fill a tiny ext4-backed gocryptfs mount and verify both writers get `ENOSPC` without truncating readable data.
- `TestAcl` uses `setfacl`/`getfacl` to verify read/write permission changes for another uid.
- `TestOverlay` mounts overlayfs on directories inside gocryptfs.
- `TestRootForceOwner` checks mkdir, create, and socket mknod as a forced owner.

## Control Flow
Tests skip unless root, then either use the package mount or create nested initialized filesystems. Credential tests run callbacks as synthetic users. Disk-full tests create a loop ext4 image, mount gocryptfs inside it, and concurrently write until no space remains.

## State And Persistence
State includes process credentials, supplementary groups, temp ext4 images, nested FUSE mounts, ACL xattrs, overlay mounts, and test files. Cleanup uses defers for unmounts and image removal.

## Dependencies And Integration Points
Depends on Linux syscalls, `internal/syscallcompat`, `mkfs.ext4`, `mount`, `setfacl`, `getfacl`, overlayfs support, and the shared root harness.

## Risks And Edge Cases
`asUser` must reset saved ids as well as effective ids to avoid later FUSE permission failures. Disk-full and overlay tests are host-kernel and privilege sensitive.

## Test Signals
Signals include successful group-authorized operations, both concurrent writers receiving `ENOSPC` with readable full contents, ACL read/write transitions matching expectations, successful overlay mount, and force-owner operations succeeding as uid/gid 1234.
