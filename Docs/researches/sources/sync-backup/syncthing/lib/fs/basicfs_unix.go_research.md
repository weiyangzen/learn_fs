# sources/sync-backup/syncthing/lib/fs/basicfs_unix.go

## Purpose
Provides non-Windows `BasicFilesystem` behavior for symlinks, hide/unhide no-ops, ownership, removal, filesystem roots, and watch path normalization.

## Important APIs, Types, and Functions
Defines `alwaysOpenFlags = syscall.O_NOFOLLOW`, `CreateSymlink`, `ReadSymlink`, `Hide`, `Unhide`, `Roots`, `Lchown`, `Remove`, `unrootedChecked`, `rel`, `evalSymlinks`, and `watchPaths`.

## Control Flow
All public operations first call `f.rooted` to canonicalize and constrain root-relative names. `Lchown` parses UID/GID strings as integers and calls `os.Lchown`. `watchPaths` resolves the configured root through symlinks, roots the watched name under that canonical root, and returns a notify recursive path plus allowed root list.

## State and Persistence Behavior
Creates symlink entries, changes file ownership, or removes a rooted path. `Hide` and `Unhide` only validate root containment because Unix hiding would require renaming dot prefixes.

## Dependencies and Integration Points
Used by `basicfs.go`, `basicfs_watch.go`, and platform data/xattr code on Unix-like builds. `O_NOFOLLOW` protects final path components from symlink traversal when opening files.

## Risks
`watchPaths` depends on `filepath.EvalSymlinks`; broken symlinked roots prevent watching. `unrootedChecked` is prefix-based after root normalization, so roots must include a single trailing separator to avoid sibling false positives. Ownership parsing rejects non-numeric IDs on Unix.

## Test Signals
Covered by `basicfs_test.go`, `basicfs_watch_test.go`, and symlink walk tests.
