# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncoffsets.c

## Purpose

`ncoffsets.c` provides a generic access layer over several directory-query and directory-notification record formats. NameChanger uses it to rewrite directory entries without duplicating structure-specific pointer arithmetic.

## Functions

- `NcDetermineStructureOffsets` fills `DIRECTORY_CONTROL_OFFSETS` for supported directory information classes: `FileBothDirectoryInformation`, `FileDirectoryInformation`, `FileFullDirectoryInformation`, `FileIdBothDirectoryInformation`, `FileIdFullDirectoryInformation`, and `FileNamesInformation`. It records offsets for `NextEntryOffset`, file-name length, file-name buffer, and optional short-name fields.
- `NcCalculateDirectoryNotificationOffsets` creates equivalent offsets for `FILE_NOTIFY_INFORMATION`.
- `NcGetNextEntryOffset`, `NcGetNextEntry`, `NcGetFileNameLength`, `NcGetEntrySize`, `NcGetFileName`, `NcGetShortName`, and `NcGetShortNameLength` read common fields using the offset table.
- `NcSetNextEntryOffset`, `NcSetFileName`, and `NcSetShortName` update records after munging names. `NcSetNextEntryOffset` can force a record to become the last entry.

## Integration

Directory enumeration and notification code use this file to parse, filter, inject, and rewrite entries for the user/real mapping relationship. It is not a validator; callers are responsible for ensuring buffers are large and well-formed enough before using these helpers.

## Risks and Notes

Record size calculation for the last entry depends on `FileNameDist + FileNameLength`, while non-last entries trust `NextEntryOffset`. Bad or malicious buffers must be handled before or around these helpers.
