# Research: sources/storage-engines/pebble/vfs/disk_usage_windows.go

## Purpose
`vfs/disk_usage_windows.go` implements Windows disk-usage reporting for `defaultFS.GetDiskUsage`.

## Important APIs, Types, And Functions
The method converts the input path with `windows.UTF16PtrFromString`, calls `windows.GetDiskFreeSpaceEx`, fills `DiskUsage.AvailBytes` and `TotalBytes`, receives total free bytes separately, and computes `UsedBytes`.

## Control Flow
If UTF-16 path conversion fails, the method returns the conversion error. Otherwise it invokes the Windows API and computes `UsedBytes = TotalBytes - freeBytes` regardless of whether the syscall returned an error; callers should inspect the returned error.

## State And Persistence
The method is read-only and reports a point-in-time view of the volume containing `path`.

## Dependencies And Integration Points
It is selected by the `windows` build tag and depends on `golang.org/x/sys/windows`. It implements VFS disk-usage reporting for Windows callers and for higher-level wrappers that delegate to the default FS.

## Risks And Edge Cases
Path conversion can fail for invalid strings. `GetDiskFreeSpaceEx` distinguishes caller-available bytes from total free bytes, so `AvailBytes` may be lower than total free under quotas. Computing `UsedBytes` after an error may leave zero values; callers must respect the error.

## Test Signals
Tests should cover invalid path conversion, syscall error propagation, normal volume accounting, quota-sensitive available bytes when feasible, and wrapper delegation.
