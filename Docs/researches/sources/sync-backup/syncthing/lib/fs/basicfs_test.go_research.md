# sources/sync-backup/syncthing/lib/fs/basicfs_test.go

## Purpose
Tests the real `BasicFilesystem` implementation against OS-backed temporary directories. It verifies path rooting, permissions, ownership, timestamps, creation, symlink behavior, directory enumeration, globbing, disk usage, xattrs, and walk integration.

## Important APIs, Types, and Functions
`setup` returns a `*BasicFilesystem` and temp root. Tests exercise `Chmod`, `Lchown`, `Chtimes`, `Create`, `CreateSymlink`, `DirNames`, `Glob`, `Usage`, `rooted`, `newBasicFilesystem`, `rel`, `GetXattr`, `SetXattr`, and walk helpers from `walkfs_test.go`. `testXattrFilter` limits xattr tests to `user.test-*`.

## Control Flow
Each test builds real filesystem state with `os` calls, invokes the `BasicFilesystem` method under test with root-relative paths, then validates OS-level results. Path-rooting tests table-drive allowed canonicalizations and rejected upward traversal. Xattr tests write a set, read it back, mutate/remove/add attributes, and verify sorted round-trip state.

## State and Persistence Behavior
State is temporary on-disk content under `t.TempDir`. Tests mutate permissions, ownership, modtimes, symlinks, xattrs, and directories. Root containment is validated without touching outside paths.

## Dependencies and Integration Points
Uses `build` platform flags, `protocol.Xattr`, `syscall`, `rand`, and shared walk tests. Platform skips handle Windows symlink/chown gaps and unsupported xattr filesystems.

## Risks
The tests rely on host filesystem capabilities, root privileges for chown, and xattr support. Some checks tolerate timestamp granularity with a three-second window. Rooting table coverage is broad and safety-critical.

## Test Signals
Strong signal for root escape prevention, path normalization, xattr reconciliation, and basic local filesystem semantics across supported platforms.
