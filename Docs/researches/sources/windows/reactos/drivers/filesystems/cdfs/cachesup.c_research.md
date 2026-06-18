# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cachesup.c

## Scope And Purpose

`cachesup.c` implements CDFS cache-manager support for internal stream files, MDL-read completion, and volume cache purging.

Complete file read: 671 lines.

## Main Components

- `CdCreateInternalStream` creates a stream file object for directory or path-table FCBs with `IoCreateStreamFileObjectLite`, initializes cache mapping with `CcInitializeCacheMap`, attaches the stream to the FCB, and gives the stream a borrowed name for profiling.
- During first stream initialization, `CdCreateInternalStream` reads the directory self entry, validates it, updates file/allocation/valid-data sizes, rebuilds initial allocation when needed, maps hidden attributes, converts CD time to NT time, and marks the FCB initialized.
- Error cleanup dereferences partially created stream objects, releases temporary dirent context, decrements the extra FCB reference, and unlocks the FCB.
- `CdDeleteInternalStream` detaches an internal stream from an FCB, uninitializes its cache map, clears the borrowed name pointer, and dereferences the file object.
- `CdCompleteMdl` completes MDL reads by calling `CcMdlReadComplete`, clearing `Irp->MdlAddress`, and completing the IRP.
- `CdPurgeVolume` closes delayed FCBs, acquires all files, walks the FCB table, flushes image sections, purges data sections, optionally deletes internal streams during dismount, and handles path-table and volume-DASD FCBs.

## Integration Points

This file is tied to Windows cache manager APIs (`CcInitializeCacheMap`, `CcUninitializeCacheMap`, `CcPurgeCacheSection`, `CcMdlReadComplete`), memory-manager image-section flushing, CDFS FCB/VCB locking, reference counting, dirent lookup, allocation helpers, and teardown logic.

## Notes

- Stream file names are borrowed from FCB-owned buffers and explicitly nulled before object dereference.
- `CdPurgeVolume` returns the first `STATUS_UNABLE_TO_DELETE_SECTION` if purge fails because a section remains active.
- The create path carefully keeps an extra FCB reference to survive error-path close/teardown behavior.
