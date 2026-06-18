# sources/test-tools/ior/src/aiori-MMAP.c

## Purpose
Implements an IOR backend that performs transfers through a shared `mmap` mapping while reusing POSIX create/open/close/delete/file-size support.

## Important APIs, Types, and Functions
- `mmap_options_t` stores the active mapping pointer plus `madv_dont_need` and `madv_pattern` flags.
- `MMAP_options` exposes madvise controls.
- `MMAP_xfer_hints` stores hints and forwards them to `POSIX_xfer_hints`.
- `MMAP_Create` calls `POSIX_Create`, truncates to `hints->expectedAggFileSize`, and maps the file.
- `MMAP_Open` maps an existing POSIX-opened file.
- `MMAP_Xfer` copies to or from `o->mmap_ptr + offset` and optionally `msync`s per write.
- `MMAP_Close` unmaps and delegates to `POSIX_Close`.

## Control Flow
The backend uses POSIX for descriptor lifecycle, then maps the full expected aggregate size with `MAP_SHARED`. Transfer calls are simple memory copies; fsync is `msync` over either the transfer range or full mapping.

## State and Persistence
Persistent data is the underlying file. Runtime mapping state is stored in module options, so one options object effectively tracks one active mapping pointer. Durability is controlled by `msync` and POSIX close behavior.

## Dependencies and Integration Points
Requires POSIX backend declarations, `sys/mman.h`, IOR expected aggregate file size hints, and POSIX metadata helpers. It does not register mdtest metadata callbacks beyond remove/file-size.

## Risks and Edge Cases
- Pointer arithmetic on `void *` is a compiler extension; strictly conforming C would require a `char *` cast.
- Mapping size comes from `expectedAggFileSize`; incorrect planning can cause out-of-bounds transfer copies.
- Per-write sync requires transfer size page alignment by `MMAP_check_params`.
- Storing mapping pointer in options can break if one options object is used for multiple concurrent open files.

## Test Signals
Test create truncation size, read/write correctness through mapping, full and per-write `msync`, madvise random/sequential/DONTNEED options, page-alignment validation, and multiple file handles sharing one options object.
