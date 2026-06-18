# File Research: sources/windows/windows-driver-samples/filesys/cdfs/fileinfo.c

## Purpose

Implements CDFS file-information query/set handling and fast I/O query callbacks. Since CDFS is read-only, set support is limited to current file position.

## Main Entry Points

- `CdCommonQueryInfo`
- `CdCommonSetInfo`
- `CdFastQueryBasicInfo`
- `CdFastQueryStdInfo`
- `CdFastQueryNetworkInfo`
- `CdQueryBasicInfo`
- `CdQueryStandardInfo`
- `CdQueryInternalInfo`
- `CdQueryEaInfo`
- `CdQueryPositionInfo`
- `CdQueryNameInfo`
- `CdQueryAlternateNameInfo`
- `CdQueryNetworkInfo`

## Query Path

`CdCommonQueryInfo` decodes the file object and supports only `UserFileOpen` and `UserDirectoryOpen`. It acquires the FCB shared, initializes an uninitialized directory stream when needed, verifies the FCB, dispatches by information class, sets `IoStatus.Information` to bytes consumed, releases the FCB, and completes the IRP.

Supported query classes include:

- `FileAllInformation`
- `FileBasicInformation`
- `FileStandardInformation`
- `FileInternalInformation`
- `FileEaInformation`
- `FilePositionInformation`
- `FileNameInformation`
- `FileAlternateNameInformation`
- `FileNetworkOpenInformation`

Name-bearing classes are rejected for `CCB_FLAG_OPEN_BY_ID` because the handle cannot supply a normal path name. `FileAllInformation` also rejects open-by-ID handles.

## Returned Metadata

`CdQueryBasicInfo` sets creation, last-write, and change time from `Fcb->CreationTime`; last-access time is zero. Attributes come from `Fcb->FileAttributes`.

`CdQueryStandardInfo` reports one link, delete-pending false, directory flag based on attributes, zero sizes for directories, and FCB allocation/file size for files.

`CdQueryInternalInfo` returns `Fcb->FileId`.

`CdQueryEaInfo` always returns EA size zero.

`CdQueryPositionInfo` returns `FileObject->CurrentByteOffset`.

`CdQueryNameInfo` copies `FileObject->FileName` into a `FILE_NAME_INFORMATION` buffer and returns `STATUS_BUFFER_OVERFLOW` if the full name does not fit while still reporting the required length.

`CdQueryNetworkInfo` returns the same timestamp/attribute/size shape used by basic and standard queries.

## Alternate Name Handling

`CdQueryAlternateNameInfo` generates the 8.3 alternate name for long names. It returns `STATUS_OBJECT_NAME_NOT_FOUND` for the root FCB, handles opened with an explicit version, or names already in 8.3 form.

For directories, it finds the child dirent by reading the path-table entry, converting the path-entry name, and searching the parent directory. For files, it looks up the raw dirent offset from the FID and converts the dirent name. It then generates the short name from the long case-normalized name and dirent offset, copies as much as fits, and reports `STATUS_BUFFER_OVERFLOW` on truncation.

## Set Path

`CdCommonSetInfo` supports only `FilePositionInformation` on `UserFileOpen`. For `FO_NO_INTERMEDIATE_BUFFERING`, the requested byte offset must align to the VCB block mask. On success it updates `FileObject->CurrentByteOffset` under the FCB lock. All other set-info requests return `STATUS_INVALID_PARAMETER`.

## Fast I/O

The three fast query routines decode the file object with `CdFastDecodeFileObject`, allow user files and initialized user directories, acquire the FCB resource shared with the caller's wait preference, verify the FCB, fill the output buffer directly from FCB fields, set `IoStatus`, release the resource, and leave the filesystem critical region. If decode, initialized-directory checks, acquisition, or verification fail, they return `FALSE` so the caller can use the normal IRP path.

## Dependencies

This file depends on file-object decoding, FCB resource synchronization, directory stream creation, dirent/path lookup helpers, 8.3 name helpers, and standard NT file-information structures.
