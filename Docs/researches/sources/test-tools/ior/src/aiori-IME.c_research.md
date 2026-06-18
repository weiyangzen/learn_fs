# sources/test-tools/ior/src/aiori-IME.c

## Purpose
Implements the IOR `IME` backend for DDN Infinite Memory Engine native APIs, including optional direct I/O, transfers, metadata, statfs, mknod, sync, and mdtest support depending on native API version.

## Important APIs, Types, and Functions
- `ime_options_t` stores `direct_io`; `IME_Options` exposes `ime.odirect`.
- `IME_Initialize` and `IME_Finalize` guard `ime_native_init`/`ime_native_finalize` with a boolean.
- `IME_Open` maps IOR flags to native open flags and optionally sets direct I/O.
- `IME_Xfer` loops over `ime_native_pwrite` or `ime_native_pread`, handles partial transfers, and optionally fsyncs per write.
- `IME_Fsync`, `IME_Close`, `IME_Delete`, `IME_GetFileSize`, and `IME_Stat` wrap native calls.
- API-version gates enable statfs/mkdir/rmdir for version >= 130 and mknod/sync for version >= 132.

## Control Flow
Create delegates to open. Transfers are positional, retry short transfers up to `MAX_RETRY`, and abort MPI when `singleXferAttempt` is set. Finalization is idempotent by `ime_initialized`.

## State and Persistence
Persistent data lives in IME. Runtime state is a global hints pointer, a global initialization boolean, and per-open heap-allocated integer descriptors. Fsync and sync are explicit native calls.

## Dependencies and Integration Points
Requires `ime_native.h`, IOR utilities, MPI globals, and POSIX-like flags. Registers both current name `IME` and legacy name `IM`.

## Risks and Edge Cases
- `IME_Xfer` does not check write `rc < 0` before partial-transfer logic, so negative write errors reach assertions after warning logic.
- Direct I/O relies on shared `set_o_direct_flag`.
- Metadata support depends heavily on `IME_NATIVE_API_VERSION`; older builds return warnings and failures for statfs/mkdir/rmdir/sync/mknod.
- `IME_GetVersion` returns a static buffer overwritten on each call.

## Test Signals
Build/test across native API versions, direct I/O, partial transfer retry/abort, fsync-per-write, initialization idempotence, statfs/mkdir/rmdir gates, mknod/sync gates, and mdtest operations.
