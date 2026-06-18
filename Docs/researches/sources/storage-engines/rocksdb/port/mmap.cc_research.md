# Research: sources/storage-engines/rocksdb/port/mmap.cc

## Purpose
This file implements `MemMapping`, RocksDB's RAII wrapper around anonymous memory mappings. It provides lazy-zeroed mappings and best-effort huge-page mappings across POSIX and Windows.

## Important APIs, Types, And Functions
The key methods are `MemMapping::~MemMapping`, move constructor, move assignment, `MemMapping::AllocateAnonymous`, `MemMapping::AllocateHuge`, and `MemMapping::AllocateLazyZeroed`. POSIX builds use `mmap`/`munmap`; Windows builds use `CreateFileMapping`, `MapViewOfFile`, `UnmapViewOfFile`, and `CloseHandle`.

## Control Flow
Destruction unmaps `addr_` when present and closes the Windows page-file handle when present. Move assignment guards self-assignment, destroys the current mapping, byte-copies the source object into the destination, and placement-news the source back to an empty `MemMapping`, transferring ownership without double-unmapping.

`AllocateAnonymous` initializes a default empty mapping, stores the requested length, returns immediately for zero length, optionally selects huge-page flags, then calls the platform mapping API. POSIX maps private anonymous read/write memory and normalizes `MAP_FAILED` to `nullptr`. Windows creates a page-file mapping and then maps a writable view.

## State And Persistence Behavior
State is `addr_`, `length_`, and on Windows `page_file_handle_`. The mapping is anonymous process memory, not file-backed persistent storage. `AllocateLazyZeroed` relies on operating-system zero-fill and possible overcommit; `AllocateHuge` requests huge pages when compile-time support exists but returns a null address on failure rather than throwing.

## Dependencies And Integration Points
The implementation depends on `port/mmap.h`, platform memory APIs, `assert`, placement new, and `Slice` exposure from the header. Callers use this for large in-memory arrays or buffers where lazy zeroing or huge pages can reduce initialization overhead or improve locality.

## Risks And Edge Cases
Failure is represented as `Get()==nullptr` while `Length()` still records the requested size, so callers must check the pointer before use. Huge-page support is compile-time and runtime dependent; requesting huge pages can fail because of OS policy, privileges, or pool size. The destructor asserts `munmap` success but otherwise ignores errors. Move assignment uses `memcpy` over the object, which is currently safe only because the class owns raw handles and no non-trivial members.

## Test Signals
Useful tests allocate zero, small, and large mappings; validate zero initialization; write/read the memory; move mappings; and verify no double unmap under sanitizers. Platform tests should cover huge-page failure fallback and Windows handle cleanup.
