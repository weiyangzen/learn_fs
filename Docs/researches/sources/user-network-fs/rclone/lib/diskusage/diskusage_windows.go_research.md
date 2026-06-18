# sources/user-network-fs/rclone/lib/diskusage/diskusage_windows.go

## Purpose
This Windows implementation reports disk usage with the Win32 `GetDiskFreeSpaceEx` API.

## Important APIs, types, and functions
- Build constraint: `windows`.
- `New(dir string) (Info, error)` converts the path to UTF-16 and fills `Available`, `Total`, and `Free`.

## Control flow
`New` calls `windows.StringToUTF16Ptr(dir)`, then `windows.GetDiskFreeSpaceEx(dir16, &info.Available, &info.Total, &info.Free)`, returning the populated `Info` and syscall error.

## State and persistence behavior
No state is persisted. The result is a live volume-space snapshot.

## Dependencies and integration points
It depends on `golang.org/x/sys/windows` and implements the common diskusage API for Windows builds.

## Risks and edge cases
The Win32 API's argument order distinguishes caller-available bytes from total and total-free bytes; this file maps that order directly to `Info`. Invalid paths, inaccessible drives, or special device paths return Windows errors.

## Test signals
`diskusage_test.go` runs on Windows and validates basic totals.
