# sources/sync-backup/syncthing/lib/fs/basicfs_windows.go

## Purpose
Implements Windows-specific `BasicFilesystem` behavior: hidden attributes, drive roots, read-only removal retry, ownership via SIDs, path canonicalization, 8.3 short-name resolution, and watch path preparation.

## Important APIs, Types, and Functions
Defines `alwaysOpenFlags = 0`, `errNotSupported`, `ReadSymlink`, `CreateSymlink`, `Hide`, `Unhide`, `Roots`, `Lchown`, `Remove`, `unrootedChecked`, `rel`, `resolveWin83`, `isMaybeWin83`, `getFinalPathName`, `evalSymlinks`, and `watchPaths`.

## Control Flow
Hide/unhide fetch and mutate Windows attributes. `Roots` calls `GetLogicalDriveStringsA`. `Remove` retries after clearing read-only permissions. `unrootedChecked` normalizes case and possible 8.3 names before root matching. `evalSymlinks` falls back to `GetFinalPathNameByHandleW`, trims Win32 namespace prefixes, and applies long filename support. `watchPaths` allows both canonicalized and user-provided roots for event matching.

## State and Persistence Behavior
Mutates filesystem attributes, ownership security descriptors, and deletes files. Watch helpers maintain no persistent state.

## Dependencies and Integration Points
Uses `golang.org/x/sys/windows`, raw Win32 syscalls, `UnicodeLowercaseNormalized`, `WindowsTempPrefix`, and notify watcher setup.

## Risks
The `Lchown` group branch parses `uid` instead of `gid`, which can break group-only ownership changes. Symlinks are unsupported here. Windows path namespace and short-name handling are complex and require broad platform tests.

## Test Signals
`basicfs_windows_test.go` covers root normalization, 8.3 detection/resolution, case-insensitive rel/unrooting, final path lookup, and read-only directory removal.
