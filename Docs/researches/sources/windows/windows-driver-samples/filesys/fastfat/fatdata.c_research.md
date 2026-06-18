# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fatdata.c

This file defines FastFAT global data and implements common request-control helpers: exception filtering/processing, request completion, top-level IRP marking, fast I/O metadata paths, and corruption popups.

Global state defined here:
- `FatData`, the main filesystem-wide state record.
- Filesystem device objects for disk and CD-ROM FAT.
- Common `LARGE_INTEGER` constants, FAT time constants, and magic divisors for time conversion.
- `FatFastIoDispatch`.
- Nonpaged lookaside lists for IRP contexts, nonpaged FCBs, and resources.
- Close-context SList and close queue mutex.
- Reserve MDL/event for paging-file forward progress.
- Disk accounting state.
- Debug/performance globals under `FASTFATDBG` and `DBG`.

Key routines:
- `FatBugCheckExceptionFilter` is debug-only and bugchecks on unexpected exceptions.
- `FatExceptionFilter` normalizes exception status, unwraps `STATUS_IN_PAGE_ERROR`, records expected statuses into the IRP context, forces waitability for cleanup, disables write-through where appropriate, and bugchecks on unexpected kernel exceptions.
- `FatProcessException` is the central exception completion path. It aborts MDL writes, unpins repinned BCBs, posts wait-required or verify-required requests when necessary, performs verify handling, raises hard errors for user-induced media/device conditions, marks volumes dirty or surface-test dirty on corruption/media failures, and completes the IRP.
- `FatCompleteRequest_Real` unpins repinned BCBs, deletes the IRP context, zeroes information on failed input operations, sets final status, and calls `IoCompleteRequest`.
- `FatIsIrpTopLevel` sets the current IRP as top-level when no top-level IRP exists.
- `FatFastIoCheckIfPossible` accepts only user file opens, checks byte-range locks for read/write, and rejects fast writes on write-protected volumes.
- `FatFastQueryBasicInfo` fills `FILE_BASIC_INFORMATION` from an FCB/DCB when the object is healthy and lock acquisition succeeds.
- `FatFastQueryStdInfo` fills `FILE_STANDARD_INFORMATION`, avoiding slow allocation lookup when allocation size is still unknown.
- `FatFastQueryNetworkOpenInfo` combines time, attribute, allocation, and EOF metadata for network-open fast path.
- `FatPopUpFileCorrupt` raises an informational hard error for corrupt non-root files, resolving the full name first and avoiding blocking system threads.

Important behavior:
- The exception path distinguishes recursive/cache-top-level calls from top-level filesystem calls.
- Verify-required errors are handled through `FatPerformVerify` when possible.
- User-induced errors can result in `IoRaiseHardError`; corruption-like statuses can mark the volume dirty.
- Fast I/O paths are conservative: they return false unless object type, FCB state, locking, and cached allocation information are all suitable.
- Root DCBs get synthesized metadata rather than normal dirent-derived timestamps/sizes.

Role in the subset:
- This file shows how a Windows filesystem driver centralizes global state, exception discipline, I/O completion, fast metadata queries, and dirty-volume escalation around NT I/O manager and cache manager contracts.
