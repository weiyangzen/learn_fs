<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_map.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_map.c

## Purpose
Implements Windows explicit memory mapping and unmapping for file handles.

## Important APIs, Types, and Functions
`__wti_win_map` uses `CreateFileMappingW` and `MapViewOfFile`; `__wti_win_unmap` uses `UnmapViewOfFile` and `CloseHandle`.

## Control Flow
Map gets file size, chooses read-only or read/write mapping protections from handle access, creates a mapping object, maps a view for the full file length, and returns both the view and mapping cookie. Unmap releases the view and closes the mapping handle.

## State and Persistence Behavior
No WiredTiger state is persisted. The mapping cookie is required to close the kernel mapping object after unmapping.

## Dependencies and Integration Points
Installed into Windows file handles by `os_fs.c`. Depends on `WT_FILE_HANDLE_WIN`, `__wti_win_fs_size`, and Windows error formatting.

## Risks and Edge Cases
Callers must prevent concurrent incompatible file-size changes. `__wti_win_unmap` treats `mapped_cookie` as a pointer to a handle slot, which must match the caller's cookie storage convention. Zero-length file mapping behavior needs coverage.

## Test Signals
Mapped read/write tests, unmap cleanup checks, zero-length/error paths, and cookie-handle leak tests are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_map.c -->
