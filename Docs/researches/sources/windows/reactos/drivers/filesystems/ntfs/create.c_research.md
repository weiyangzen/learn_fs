# File Research: sources/windows/reactos/drivers/filesystems/ntfs/create.c

Read status: complete file, 963 lines.

This file implements `IRP_MJ_CREATE`: volume opens, file opens by name or ID, overwrite handling, reparse handling, and experimental file/directory creation.

Key entry points:
- `NtfsMakeAbsoluteFilename()` converts related-file-object opens into absolute paths.
- `NtfsMoonWalkID()` reconstructs a path from an MFT ID by walking parent filename attributes back to root.
- `NtfsOpenFileById()` opens reserved/system MFT entries by ID using the `MftIdToName` table.
- `NtfsOpenFile()` resolves an absolute path, checks the FCB table, and calls `NtfsGetFCBForFile()` when needed.
- `NtfsCreateFile()` is the main create/open routine. It validates options, denies opens when the volume is locked, handles `FILE_OPEN_BY_FILE_ID`, volume opens, existing-file disposition checks, directory/non-directory constraints, reparse points, overwrite truncation, and new file/directory creation when write support is enabled.
- `NtfsCreate()` queues non-waitable creates, then serializes create/open under `DirResource`.
- `NtfsCreateDirectory()` builds a new directory file record with standard information, filename, and empty `$I30` index root, adds it to the MFT, then inserts its filename into the parent directory index.
- `NtfsCreateEmptyFileRecord()` initializes a blank FILE record with USA metadata and an attribute-end marker.
- `NtfsCreateFileRecord()` builds a normal file record with `$STANDARD_INFORMATION`, `$FILE_NAME`, and `$DATA`, then adds it to the parent directory.

Important dependencies:
- FCB lookup and attach: `NtfsGrabFCBFromTable`, `NtfsGetFCBForFile`, `NtfsAttachFCBToFileObject`.
- MFT/file-record helpers: `ReadFileRecord`, `AddNewMftEntry`, `AddStandardInformation`, `AddFileName`, `AddData`.
- Directory index mutation: `CreateEmptyBTree`, `CreateIndexRootFromBTree`, `AddIndexRoot`, `NtfsAddFilenameToDirectory`.
- Write gate: `NtfsGlobalData->EnableWriteSupport`.

Notable behavior and risks:
- Path canonicalization is still TODO; `.`/`..` and repeated separators are not normalized here.
- New creation and overwrite are denied unless experimental write support is enabled.
- Open-by-ID for user files reconstructs a path, while reserved system IDs use a fixed name table. The diagnostic print for open-by-ID references `FullPath` even when the system-ID path was used.
- Reparse support recognizes mount points and otherwise returns `STATUS_NOT_IMPLEMENTED`.
