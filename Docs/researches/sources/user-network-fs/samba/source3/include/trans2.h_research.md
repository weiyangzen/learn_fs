# sources/user-network-fs/samba/source3/include/trans2.h

## Purpose
`trans2.h` defines SMB1 Transaction2, NT passthrough, FSCC file-information, filesystem-information, directory-search, and related info-level constants and legacy structure offsets. It is a protocol layout header for SMB1 query/set path/file/fs info and findfirst/findnext handlers.

## Important APIs, Types, and Constants
- Legacy DOS find/status offsets: `l1_*`, `l2_*`, `l260_achName`, FS allocation/volume offsets, and `DIRLEN_GUESS`.
- SMB info levels: `SMB_INFO_STANDARD`, `SMB_INFO_QUERY_EA_SIZE`, `SMB_QUERY_FS_*`, `SMB_QUERY_FILE_*`, `SMB_FIND_*`, and `SMB_SET_FILE_*`.
- Device and characteristic constants: `DEVICETYPE_*`, `TYPE_*`, `FILE_DEVICE_*`, and `FILE_*` characteristics.
- Sector-size info constants: `SSINFO_FLAGS_*` and `SSINFO_OFFSET_UNKNOWN`.
- FSCC classes: `FSCC_FILE_*` and `FSCC_FS_*`, including Samba's POSIX info placeholder class `100`.
- NT passthrough mapping: `NT_PASSTHROUGH_OFFSET`, `SMB_FILE_*`, `SMB_FS_*`, and internal SMB2 special levels.
- Find flags: `FLAG_TRANS2_FIND_CLOSE`, `FLAG_TRANS2_FIND_CLOSE_IF_END`, `FLAG_TRANS2_FIND_REQUIRE_RESUME`, `FLAG_TRANS2_FIND_CONTINUE`, and `FLAG_TRANS2_FIND_BACKUP_INTENT`.

## Control Flow and State
This header has no functions, but it drives transaction dispatch and marshalling. Request handlers compare incoming info levels against these constants, choose parser/encoder paths, and write legacy response buffers using the offset macros.

## Persistence Behavior
No direct persistence. Some info levels declared here trigger file metadata mutation in setfile/setpathinfo handlers, including allocation size, EOF, disposition/delete-on-close, basic timestamps, and filesystem metadata where supported.

## Dependencies and Integration Points
It integrates with SMB1 `TRANS2_*` handlers, SMB2 getinfo/setinfo compatibility mapping, FSCC marshalling, directory enumeration, stream info, quota/object-id handling, and Mac CIFS extension handling.

## Risks
- Constants are wire protocol values; changing them breaks client compatibility.
- Legacy offset macros must match packed wire structures, independent of compiler struct packing.
- NT passthrough offset mapping must stay aligned with FSCC class values and Samba internal special levels.
- Unsupported or undefined info levels must be rejected predictably to avoid malformed response buffers.

## Test Signals
SMB1 trans2 torture tests, query/set path/file/fs info tests, directory enumeration info-level coverage, Mac extension tests if enabled, SMB2 getinfo/setinfo mapping tests, and fuzzing malformed trans2 buffers.
