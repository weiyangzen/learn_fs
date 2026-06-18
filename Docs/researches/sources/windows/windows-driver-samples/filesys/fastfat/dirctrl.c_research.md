# File Research: sources/windows/windows-driver-samples/filesys/fastfat/dirctrl.c

Read fully: 1,608 lines.

This file implements FastFAT directory-control dispatch. It handles `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`, including wildcard query template setup, short-name and long-name matching support, output buffer packing for multiple Windows directory information classes, FAT timestamp conversion, and registration of directory-change notifications.

Core responsibilities:
- Dispatch directory-control IRPs from FSD entry to common worker logic.
- Validate directory opens and query parameters.
- Maintain per-handle enumeration state in the CCB.
- Convert query patterns into uppercase Unicode and OEM/8.3 forms.
- Iterate matching FAT directory entries with `FatLocateDirent`.
- Format directory entries into caller-selected information structures.
- Register change-notification requests through FsRtl notify support.

Major routines:
- `FatFsdDirectoryControl` is the FSD dispatch entry. It enters filesystem context, establishes top-level IRP state, creates an IRP context using synchronous wait capability, calls `FatCommonDirectoryControl`, and routes exceptions through FastFAT exception processing.
- `FatCommonDirectoryControl` switches on the minor function and calls `FatQueryDirectory` or `FatNotifyChangeDirectory`; unsupported minor functions complete with `STATUS_INVALID_DEVICE_REQUEST`.
- `FatQueryDirectory` is the main enumeration engine. It validates `UserDirectoryOpen`, maps the user buffer, acquires the DCB shared or exclusive depending on initial/restart query state, builds or resets the CCB query template, scans directory entries, formats results, updates `Ccb->OffsetToStartSearchFrom`, and completes the IRP.
- `FatGetDirTimes` fills `FILE_DIRECTORY_INFORMATION` timestamps from a FAT dirent. It always computes last-write time and, in Chicago mode, also derives creation and last-access times with fast paths for common same-date/time cases and defaults to Jan 1, 1980 when FAT fields are zero.
- `FatNotifyChangeDirectory` validates a directory open, acquires the DCB exclusively, ensures the full name is present, rejects delete-pending directories, and passes the request to `FsRtlNotifyFullChangeDirectory`.

Directory query behavior:
- Initial query or restart scan acquires the DCB exclusively because it may mutate the CCB’s search template.
- Subsequent scans use `Ccb->OffsetToStartSearchFrom` unless `SL_INDEX_SPECIFIED` or `SL_RESTART_SCAN` changes the starting VBO.
- Match-all is selected for no filename, empty filename, `*`, or DOS `????????.???`.
- Non-match-all templates are upcased and stored as Unicode, with a best-fit OEM representation when possible.
- If the query contains extended Unicode that cannot map to OEM, FastFAT skips short-name comparison instead of failing for `STATUS_UNMAPPABLE_CHARACTER`.
- For non-wildcard OEM names, the template is converted to an 8.3 constant with `FatStringTo8dot3`.
- Wildcards retain the OEM wildcard string in `Ccb->OemQueryTemplate.Wild`.

Supported output classes:
- `FileDirectoryInformation`
- `FileFullDirectoryInformation`
- `FileIdFullDirectoryInformation`
- `FileNamesInformation`
- `FileBothDirectoryInformation`
- `FileIdBothDirectoryInformation`

Output formatting details:
- The routine computes each class’s base structure length using `FIELD_OFFSET(..., FileName[0])`.
- For short-name-only entries, it converts the FAT 8.3 OEM name to Unicode with `RtlOemToUnicodeN`.
- For long-name entries, it copies the located long Unicode filename directly.
- Both-directory classes also include the converted short name in `ShortName`.
- Full-directory classes attempt to read EA size with `FatGetEaLength`; corrupt EA failures are swallowed and reported as `EaSize = 0` so enumeration continues.
- File ID classes fill `FileId` with `FatGenerateFileIdFromDirentAndOffset`.
- `NextEntryOffset` is written into the previous record, entries are quad-aligned, and buffer-overflow behavior follows Windows directory-query rules: a too-large first record may return partial name plus `STATUS_BUFFER_OVERFLOW`, while later non-fitting records are left for the next query.

Important implementation details:
- The code protects user-buffer writes with exception handling because directory queries are not necessarily buffered by the I/O manager.
- `UpdateCcb` is suppressed on exceptions or end-of-directory failures where the enumeration position should not advance.
- `InitialQuery` returning no match produces `STATUS_NO_SUCH_FILE`; later exhaustion produces `STATUS_NO_MORE_FILES`.
- Directory allocation size is reported as zero for directories and cluster-rounded file size for ordinary files.
- Dirents with no attributes are reported as `FILE_ATTRIBUTE_NORMAL`.
- The notify path stores no result buffer itself; once FsRtl owns the IRP, FastFAT completes only the IRP context and returns `STATUS_PENDING`.

Research relevance:
This file shows the Windows FAT directory-control contract in detail: persistent per-handle enumeration state, DOS/Unicode name matching, 8.3 and long-name result formatting, precise query-buffer packing semantics, FAT timestamp adaptation, and FsRtl-based directory notification integration.
