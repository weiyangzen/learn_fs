# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nccompat.c

This file provides runtime compatibility shims so the sample can run across multiple Windows/FltMgr versions. It resolves newer APIs dynamically and falls back to local implementations when unavailable.

Global function pointers initialized here:
- `NcReplaceFileObjectName`
- `NcQueryDirectoryFile`
- `NcCreateFileEx2`
- `NcGetNewSystemBufferAddress`
- Internal fallback pointer `NcCreateFileEx`

`NcReplaceFileObjectNameAlternate` replaces `FileObject->FileName` on systems without `IoReplaceFileObjectName`. If the existing buffer is large enough it zeroes and reuses it; otherwise it allocates a new paged-pool buffer and frees the old one. The comments note verifier can report false pool leaks on older systems because this bypasses the newer kernel helper.

`NcQueryDirectoryFileAlternate` emulates `FltQueryDirectoryFile` by allocating callback data, setting up an `IRP_MJ_DIRECTORY_CONTROL / IRP_MN_QUERY_DIRECTORY` operation, applying `SL_RESTART_SCAN` and `SL_RETURN_SINGLE_ENTRY` as needed, performing synchronous I/O, optionally returning bytes read, then freeing callback data.

`NcCreateFileEx2Alternate` emulates `FltCreateFileEx2`. It rejects transaction/create-context support by assertion, uses `FltCreateFileEx` if available, otherwise falls back to `FltCreateFile` and optionally references the returned file object by handle. On failure it closes/dereferences partial outputs.

`NcCompatInit` opts into NX nonpaged pool where supported, resolves `IoReplaceFileObjectName` through `MmGetSystemRoutineAddress`, resolves FltMgr routines through `FltGetRoutineAddress`, and installs fallbacks as needed.

Important dependencies:
- Used by `DriverEntry` before mapping initialization and filter registration.
- The rest of the driver calls the function pointers directly, avoiding scattered OS-version checks.

Notable behavior:
- Transaction/ECP support depends on real `FltCreateFileEx2`; fallback asserts that `DriverContext == NULL`.
- `NcGetNewSystemBufferAddress` may remain `NULL` if unavailable; callers must tolerate that.
