<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read_write_test.go -->
# sources/user-network-fs/rclone/vfs/read_write_test.go

## Purpose
Tests cache-backed `RWFileHandle` behavior for read-only, write-only, read/write open modes, size tracking, truncation, open flag compatibility, modtime writeback, cache rename, and cache refresh after external remote updates.

## Important APIs, Types, and Functions
Helpers include `rwHandleCreateFlags`, `rwHandleCreateReadOnly`, `rwHandleCreateWriteOnly`, `rwReadString`, `assertSize`, and `testRWFileHandleOpenTest`. Main tests cover methods, seek/read/read-at, flush/release, write/write-at/no-write, size cases, generated open matrix, modtime with open writers, rename, and cache update.

## Control Flow
Most tests create a full-cache VFS with short writeback delay, perform handle operations, close or release, wait for writers, and validate VFS listing plus remote contents. The open matrix creates nonexistent and existing files for each generated `openTest`, probes reads/writes, and compares expected errors and final contents for both `CacheModeWrites` and `CacheModeFull`.

## State and Persistence Behavior
Tests validate local cache state, remote upload state after writer drain, `File.Size` visibility while handles are open, dirty empty-file creation, pending modtime application, and cache item rename after VFS rename. `TestRWCacheUpdate` verifies cache and stat data refresh after external remote content changes and directory cache expiry.

## Dependencies and Integration Points
Uses `open_test.go`, `operations.CanServerSideMove`, `fstest`, VFS cache/writeback options, and shared test helpers. It exercises integration among `VFS.OpenFile`, `File.Open`, `RWFileHandle`, `vfscache.Item`, directory cache, and remote listing.

## Risks and Edge Cases
Coverage is strongest for cache modes, not uncached streaming writes. Some behavior depends on backend support for empty uploads, modtime precision, and server-side move. Concurrent RW handles and writeback failure recovery are not deeply covered here.

## Test Signals
Very strong signal for cached file handle semantics, POSIX-like open flag behavior, size and truncation correctness, and cache coherency after rename/external updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read_write_test.go -->
