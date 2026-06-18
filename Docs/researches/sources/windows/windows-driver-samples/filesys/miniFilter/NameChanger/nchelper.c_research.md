# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nchelper.c

## Purpose

`nchelper.c` contains small cross-cutting helpers used across the NameChanger minifilter.

## Functions

- `NcGetFileNameInformation` wraps `FltGetFileNameInformation` and `FltGetFileNameInformationUnsafe`, selecting the safe callback-data path when `Data` is available and the unsafe file-object/instance path otherwise.
- `NcAllocateEResource` allocates a nonpaged `ERESOURCE`, initializes it with `ExInitializeResourceLite`, and cleans up correctly on partial failure.
- `NcFreeEResource` deletes and frees an `ERESOURCE` allocated by `NcAllocateEResource`.
- `NcCreateFileHelper` wraps `NcCreateFileEx2`. On Longhorn+ builds it initializes `IO_DRIVER_CREATE_CONTEXT` and propagates transaction parameters from a parent file object so internal creates remain transaction-aware.
- `NcSetCancelCompletion` synchronizes cancellation callback setup with the global cancel spin lock and returns `STATUS_CANCELLED` if the operation was already canceled.
- `NcExceptionFilter` centralizes exception filtering for user-buffer access. Unexpected exceptions continue searching unless the caller explicitly says it was accessing user memory.

## Integration

These helpers are used by FSCTL, directory enumeration/notification, file information, mapping, and name-provider paths. The create helper is especially important for internal opens of mapping parents and real-mapping directories.

## Risks and Notes

The file is intentionally low-level. Correct call-site discipline matters: callers must release file-name information, free allocated resources, and only pass user-buffer exceptions through `NcExceptionFilter` when they are intentionally probing or copying user memory.
