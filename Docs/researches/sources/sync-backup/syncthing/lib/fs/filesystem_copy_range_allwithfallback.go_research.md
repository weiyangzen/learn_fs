# sources/sync-backup/syncthing/lib/fs/filesystem_copy_range_allwithfallback.go

## Purpose
Registers and implements a fallback chain that tries all copy-range strategies before giving up.

## Important APIs, Types, and Functions
`init` registers `CopyRangeMethodAllWithFallback`. `copyRangeAllWithFallback` tries ioctl, copy_file_range, sendfile, duplicate extents, then standard copy.

## Control Flow
The method calls `CopyRange` recursively for each concrete method and returns nil on first success. If all fail, it returns the last error.

## State and Persistence Behavior
Destination file may be partially modified by a failed earlier method if that implementation has side effects before erroring. The wrapper itself stores no state.

## Dependencies and Integration Points
Depends on registered concrete methods. Useful when callers prefer best-effort acceleration with standard fallback.

## Risks
Returning only the last error can hide the true best diagnostic from earlier methods. Partial writes before fallback are a concern if implementations are not all-or-nothing.

## Test Signals
Copy-range tests include `AllWithFallback` in expected error and success matrices.
