# File Research: sources/windows/reactos/drivers/filesystems/fastfat/dirctrl.c

## Purpose

`dirctrl.c` implements FAT directory-control IRP handling: `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`. It is the dispatch-facing layer that validates directory opens, manages query templates stored in the CCB, streams directory entries into the caller’s buffer in requested NT information formats, and registers directory change notifications with FSRTL.

## Main Entry Points

- `FatFsdDirectoryControl` is the FSD dispatch entry. It enters the filesystem, creates an IRP context with wait permission derived from the IRP, calls `FatCommonDirectoryControl`, and routes exceptions through `FatProcessException`.
- `FatCommonDirectoryControl` switches on the minor function and calls either `FatQueryDirectory` or `FatNotifyChangeDirectory`.
- `FatQueryDirectory` implements directory enumeration and wildcard matching.
- `FatGetDirTimes` converts FAT on-disk timestamp fields into NT `LARGE_INTEGER` timestamps for query output.
- `FatNotifyChangeDirectory` validates a directory open, acquires the DCB, ensures the full name is available, and calls `FsRtlNotifyFullChangeDirectory`.

## Query Directory Flow

`FatQueryDirectory` accepts only `UserDirectoryOpen` file objects and rejects malformed Unicode filename lengths. It reads query parameters from the IRP stack: user buffer length, information class, file index, optional filename, restart flag, return-single-entry flag, and index-specified flag.

The query template is persisted in the CCB. On initial query or restart, the function acquires the DCB exclusively so it can update template state safely. Otherwise it acquires shared access for enumeration. If acquisition cannot wait, the request is posted to the FSP.

Template handling supports several cases:

- No filename, empty filename, `*`, or DOS `????????.???` sets `CCB_FLAG_MATCH_ALL`.
- Non-extended ASCII names are upcased manually into a combined Unicode/OEM allocation.
- Extended names use `RtlUpcaseUnicodeString` and `RtlUpcaseUnicodeStringToCountedOemString`.
- Names that cannot be represented or are not legal short OEM names set `CCB_FLAG_SKIP_SHORT_NAME_COMPARE`, forcing LFN-only matching.
- Wildcard templates are stored in `Ccb->OemQueryTemplate.Wild`; constant 8.3 templates are stored in `Ccb->OemQueryTemplate.Constant`.

The scan starting point is chosen in priority order: explicit file index, restart scan, or `Ccb->OffsetToStartSearchFrom`.

## Output Formats

The function supports:

- `FileDirectoryInformation`
- `FileFullDirectoryInformation`
- `FileIdFullDirectoryInformation`
- `FileNamesInformation`
- `FileBothDirectoryInformation`
- `FileIdBothDirectoryInformation`

It computes each format’s base length with `FIELD_OFFSET(..., FileName[0])`, then repeatedly calls `FatLocateDirent` to find the next matching entry. It fills packed variable-length records in the caller buffer using `NextEntryOffset` chaining and quad alignment.

For 8.3-only entries it converts the OEM short name to Unicode with `RtlOemToUnicodeN`. For entries with LFNs it copies the Unicode long name directly. `FileBothDirectoryInformation` and `FileIdBothDirectoryInformation` include the short name when a long name exists. `FileId*` classes use `FatGenerateFileIdFromDirentAndOffset`.

For full information classes, EA size is fetched with `FatGetEaLength`; EA corruption is deliberately ignored so enumeration continues with `EaSize = 0`.

Buffer semantics match NT directory-query rules: the first entry may be partially returned with `STATUS_BUFFER_OVERFLOW`, but later entries are omitted entirely if they do not fit and the call succeeds with entries already returned.

## Timestamp and Attribute Handling

`FatGetDirTimes` always sets last-write time from `Dirent->LastWriteTime`. In Chicago mode it also derives creation and last-access times. It has fast paths when creation/access fields match last-write data and falls back to `FatJanOne1980` when optional FAT timestamp fields are zero.

Directory query output sets:

- `EndOfFile` from `Dirent->FileSize`.
- `AllocationSize` rounded to cluster size for non-directories.
- `FileAttributes` from dirent attributes, or `FILE_ATTRIBUTE_NORMAL` when no attributes are set.
- `FileIndex` to the next VBO returned by `FatLocateDirent`, allowing continuation.

## Notify Change Flow

`FatNotifyChangeDirectory` forces wait behavior, validates `UserDirectoryOpen`, reads the completion filter and `SL_WATCH_TREE`, and acquires the DCB exclusively. It verifies the FCB, builds the full file name, rejects delete-pending directories, then calls `FsRtlNotifyFullChangeDirectory` with the volume notify list and sync object.

If FSRTL takes ownership of the IRP, the function completes only the IRP context (`FatNull` IRP) and returns `STATUS_PENDING`.

## State, Dependencies, and Side Effects

This file depends on `dirsup.c` for `FatLocateDirent`, 8.3 conversion, LFN extraction, file IDs, and EA lookup. It relies on CCB fields for persistent query templates and offsets, DCB resources for synchronization, `FatMapUserBuffer` from `deviosup.c` for safe buffer access, and FSRTL notify infrastructure for change notifications.

It mutates CCB query-template buffers and flags, `Ccb->OffsetToStartSearchFrom`, IRP status/information, and may post requests when locks cannot be acquired synchronously.

## Correctness Notes and Risks

The main correctness pressure is preserving query state across calls while allowing concurrent directory enumeration. Initial and restart queries must update CCB template state under exclusive DCB access; regular scans use shared access.

User buffer writes are wrapped in SEH because the request is not necessarily buffered by the I/O manager. On exception, the function clears `IoStatus.Information`, suppresses CCB offset updates, and completes with the exception status.

The switch statements intentionally fall through from richer directory information classes into common base-field population. Changes here must preserve that fall-through structure.

## Research Coverage

Read completely. Covered FSD/common dispatch, query-template construction, directory scan/output packing, timestamp conversion, file-ID handling, EA-size behavior, cleanup, and notify registration.
