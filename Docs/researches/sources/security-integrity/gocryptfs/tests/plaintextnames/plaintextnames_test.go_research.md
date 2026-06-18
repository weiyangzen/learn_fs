# sources/security-integrity/gocryptfs/tests/plaintextnames/plaintextnames_test.go

## Purpose
Defines integration tests specific to gocryptfs `-plaintextnames` mode, where filenames are not encrypted and several normal encrypted-name invariants change.

## Important APIs, Types, And Functions
- `TestMain` initializes and mounts a plaintextnames filesystem.
- `TestFlags` decrypts `gocryptfs.conf` and checks feature flags.
- `TestDirIV` asserts diriv files are not created in root or subdirectories.
- `TestFiltered` checks reserved root `gocryptfs.conf` filtering while allowing other magic names.
- `TestInoReuseEvil` manipulates cipherdir entries behind the mount to stress inode reuse.
- `TestRootIno` checks the root inode number is nonzero.

## Control Flow
The package-level mount is created once. Tests inspect config flags, create directories and files through the mount, and in `TestInoReuseEvil` deliberately remove and recreate backing objects to mimic inode reuse collisions.

## State And Persistence
`cDir`, `pDir`, and `testPw` are package state. The mounted filesystem persists for all package tests and is unmounted in `TestMain` after `m.Run`.

## Dependencies And Integration Points
Depends on `internal/configfile` for config verification and `test_helpers` for initialization and mounting. Uses direct `syscall` calls to test low-level behavior.

## Risks And Edge Cases
The inode reuse test relies on filesystems such as ext4 that recycle inode numbers; on others it may not reproduce the intended edge. Reserved-name behavior differs between root and subdirectories.

## Test Signals
Signals include exact feature flag set, absent diriv files, expected failures for root `gocryptfs.conf`, allowed non-root magic names, and nonzero root inode.
