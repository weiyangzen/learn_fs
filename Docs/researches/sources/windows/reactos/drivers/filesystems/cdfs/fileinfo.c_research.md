# File Research: sources/windows/reactos/drivers/filesystems/cdfs/fileinfo.c

## Purpose

`fileinfo.c` implements CDFS file-information query and set handlers, plus fast I/O query callbacks. Because CDFS is read-only, set-information support is intentionally narrow: it only accepts `FilePositionInformation` on user file opens.

## Main Dispatch Routines

- `CdCommonQueryInfo`: handles `IRP_MJ_QUERY_INFORMATION` for user file and directory opens. It acquires the FCB shared, initializes directory stream metadata if needed, verifies the FCB, dispatches by `FILE_INFORMATION_CLASS`, updates `IoStatus.Information`, releases the FCB, and completes the IRP.
- `CdCommonSetInfo`: handles `IRP_MJ_SET_INFORMATION`, but only for `FilePositionInformation` on `UserFileOpen`. It validates alignment for `FO_NO_INTERMEDIATE_BUFFERING`, then updates `FileObject->CurrentByteOffset` under the FCB lock.

## Supported Query Classes

`CdCommonQueryInfo` supports:

- `FileAllInformation`
- `FileBasicInformation`
- `FileStandardInformation`
- `FileInternalInformation`
- `FileEaInformation`
- `FilePositionInformation`
- `FileNameInformation`
- `FileAlternateNameInformation`
- `FileNetworkOpenInformation`

Name and alternate-name queries are rejected for handles opened by file ID. Unsupported classes return `STATUS_INVALID_PARAMETER`.

## Local Query Helpers

- `CdQueryBasicInfo`: zeroes `FILE_BASIC_INFORMATION`, sets creation/last-write/change time from `Fcb->CreationTime`, last access to zero, and attributes from the FCB.
- `CdQueryStandardInfo`: reports one link, not delete-pending, and returns zero allocation/EOF for directories; files use `Fcb->AllocationSize` and `Fcb->FileSize`.
- `CdQueryInternalInfo`: returns `Fcb->FileId` as the index number.
- `CdQueryEaInfo`: returns EA size zero because CDFS has no EAs.
- `CdQueryPositionInfo`: returns `FileObject->CurrentByteOffset`.
- `CdQueryNameInfo`: copies `FileObject->FileName` into `FILE_NAME_INFORMATION`, returning `STATUS_BUFFER_OVERFLOW` if only a prefix fits while preserving the required full length.
- `CdQueryAlternateNameInfo`: computes and returns a generated 8.3 alternate name for long-name files.
- `CdQueryNetworkInfo`: fills `FILE_NETWORK_OPEN_INFORMATION` with timestamps, attributes, and size fields.

## Fast I/O Query Callbacks

- `CdFastQueryBasicInfo`: fast path for basic info.
- `CdFastQueryStdInfo`: fast path for standard info.
- `CdFastQueryNetworkInfo`: fast path for network-open info.

All decode the file object, require initialized user file or directory opens, acquire the FCB resource shared with the caller’s `Wait` setting, verify the FCB, fill the output buffer, set `IoStatus`, and release the resource. If preconditions fail or the resource cannot be acquired, they return `FALSE` so the caller can use the IRP path.

## Alternate Name Lookup

`CdQueryAlternateNameInfo` is the most complex helper. It rejects root and version-specific opens, acquires the parent directory, ensures the parent stream exists, and then locates the original dirent:

- For directories, it resolves the child path-table entry and searches the parent by directory name.
- For files, it directly looks up the dirent offset encoded in the file ID.

It updates the dirent name, rejects names already legal 8.3, generates a short name with `CdGenerate8dot3Name`, copies it to the output buffer, and handles cleanup of dirent/path contexts.

## Error and Status Behavior

The file consistently uses length decrementing to compute `IoStatus.Information`. Several helper routines assume the caller provided enough fixed-structure space; variable-length name helpers explicitly return `STATUS_BUFFER_OVERFLOW` when only partial name data fits. Read-only unsupported set operations return `STATUS_INVALID_PARAMETER`.

## Dependencies

This file depends on file-object decoding from `filobsup.c`, directory lookup/name support from `dirsup.c` and `namesup.c`, FCB/VCB verification helpers, resource acquisition helpers, and Windows `FILE_*_INFORMATION` structures.

## Research Notes

The implementation preserves Windows CDFS semantics: directories report zero logical size for standard/network information, access time is zero, delete-pending is always false, EA size is zero, and alternate names are synthetic rather than on-disk metadata.
