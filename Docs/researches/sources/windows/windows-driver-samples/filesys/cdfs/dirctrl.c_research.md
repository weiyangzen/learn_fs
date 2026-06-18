# File Research: sources/windows/windows-driver-samples/filesys/cdfs/dirctrl.c

## Purpose

Implements CDFS directory-control handling for directory enumeration and directory change notification. This is the IRP_MJ_DIRECTORY_CONTROL worker used by both FSD and FSP paths.

## Main Entry Points

- `CdCommonDirControl`: validates that the handle decodes as `UserDirectoryOpen`, then dispatches on minor function.
- `CdQueryDirectory`: performs `IRP_MN_QUERY_DIRECTORY`.
- `CdNotifyChangeDirectory`: performs `IRP_MN_NOTIFY_CHANGE_DIRECTORY`.
- `CdInitializeEnumeration`: prepares persistent enumeration state from the CCB and request flags.
- `CdEnumerateIndex`: advances through directory entries until it finds the next matching visible entry.

## Key Behavior

`CdCommonDirControl` rejects non-directory handles with `STATUS_INVALID_PARAMETER`. It handles only `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`; other minor functions complete with `STATUS_INVALID_DEVICE_REQUEST`.

`CdQueryDirectory` supports these information classes:

- `FileDirectoryInformation`
- `FileFullDirectoryInformation`
- `FileIdFullDirectoryInformation`
- `FileNamesInformation`
- `FileBothDirectoryInformation`
- `FileIdBothDirectoryInformation`

It maps the user buffer, initializes a `FILE_ENUM_CONTEXT`, acquires the directory FCB shared, verifies the FCB, initializes enumeration state, then loops over matching entries. The buffer-fill rules are explicit: the first matching record may return a truncated name with `STATUS_BUFFER_OVERFLOW`; later records are either fully copied or not copied at all, preserving restart position for a later query.

Directory result entries use the dirent creation time for creation/write/change times. Directories report zero allocation and EOF and get `FILE_ATTRIBUTE_DIRECTORY`; files use the computed `FileContext.FileSize`, sector-aligned allocation, and `FILE_ATTRIBUTE_READONLY`. Hidden dirents set `FILE_ATTRIBUTE_HIDDEN`. ID directory classes receive a file ID via `CdSetFidFromParentAndDirent`.

For name output, it copies the Unicode file name and optionally appends `;` plus the version string. Version strings are returned when the search expression included a version, and also for directories with a version string. `FileBothDirectoryInformation` and `FileIdBothDirectoryInformation` also get a generated 8.3 short name when appropriate.

Enumeration state lives in the CCB. On a successful/non-error exit, after cleaning up the file context, it updates `Ccb->CurrentDirentOffset` and `CCB_FLAG_ENUM_RETURN_NEXT` under the FCB lock. Cleanup is intentionally done before acquiring the FCB mutex to avoid blocking against internal stream creation/purge paths that wait for mappings to release.

`CdNotifyChangeDirectory` supports notify requests even though CD media will not generate modifications. It verifies the VCB and calls `FsRtlNotifyFullChangeDirectory`, using the file object's name as the watched path and then completes only the IRP context while leaving the IRP pending.

## Enumeration Details

`CdInitializeEnumeration` handles restart and pattern setup. If `SL_RESTART_SCAN` includes a new pattern, it frees any previous search expression and clears initialization flags. It treats missing, empty, or single `*` names as match-all. Otherwise it converts the requested name into CDFS name/version components, records wildcard flags independently for name and version, uppercases for ignore-case searches, and stores the expression in the CCB. Root-directory enumeration suppresses constant `.` and `..` entries.

Positioning supports three modes:

- `SL_INDEX_SPECIFIED`: starts from the caller's file index and walks from the beginning to find a valid containing dirent.
- `SL_RESTART_SCAN`: starts from the directory stream offset.
- Otherwise: resumes from the CCB's saved offset and return-next flag.

`CdEnumerateIndex` skips associated files, root-suppressed constant entries, and duplicate lower versions when the search expression has no version component. It tests the long name first, then generates/tests an 8.3 short name when the long name is not 8.3 and the search has no version. On match, it calls `CdLookupLastFileDirent` so multi-extent files have complete size information.

## Dependencies

This file depends heavily on file object decoding, FCB/VCB locking, dirent walking and name conversion helpers from the rest of CDFS:

- `CdDecodeFileObject`
- `CdVerifyFcbOperation`
- `CdVerifyOrCreateDirStreamFile`
- `CdLookupInitialFileDirent`
- `CdLookupNextInitialFileDirent`
- `CdLookupLastFileDirent`
- `CdUpdateDirentName`
- `CdIsNameInExpression`
- `CdGenerate8dot3Name`
- `FsRtlNotifyFullChangeDirectory`
