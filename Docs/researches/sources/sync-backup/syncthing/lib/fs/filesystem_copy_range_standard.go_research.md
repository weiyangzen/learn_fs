# sources/sync-backup/syncthing/lib/fs/filesystem_copy_range_standard.go

## Purpose
Provides the portable copy-range implementation using `ReadAt` and `WriteAt`.

## Important APIs, Types, and Functions
`init` registers `CopyRangeMethodStandard`. `copyRangeStandard` loops with a 4 MiB buffer, reading from source offset and writing to destination offset.

## Control Flow
For each chunk, it shrinks the buffer to remaining size, reads with `ReadAt`, converts EOF to `io.ErrUnexpectedEOF`, writes the read bytes, and advances offsets until requested size reaches zero.

## State and Persistence Behavior
Writes destination contents and may extend sparse regions through `WriteAt`. It intentionally does not alter file seek positions.

## Dependencies and Integration Points
Portable fallback used directly or through `AllWithFallback`.

## Risks
Short reads without errors would still progress by `n`; EOF always aborts as unexpected. The buffer allocation is per call and can be large for frequent small copies.

## Test Signals
Copy-range tests validate offsets, appended/overwritten data, sparse gaps, full-file copies, and unexpected EOF.
