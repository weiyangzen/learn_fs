# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/Sys_spec_lib.cpp

## Purpose

`Sys_spec_lib.cpp` implements UDF-to-NT conversion and OS-specific helper logic shared by the UDFS driver support code. It translates timestamps, attributes, directory records, names, Unicode strings, cache state, and delete/rename policy between UDF metadata and NT filesystem structures.

## Main Functions

- `UDFTimeToNT`
  - Converts a UDF timestamp into NT system time.
  - Builds `TIME_FIELDS`, clamps pre-1601 years, converts local time to system time.
- `UDFTimeToUDF`
  - Converts NT time to a UDF local timestamp.
  - Fills microsecond, hundred-microsecond, centisecond, date/time, and timezone fields.
- `UDFAttributesToNT`
  - Converts UDF file-entry flags, permissions, file type, and directory-index characteristics to NT file attributes.
  - Sets system, archive, directory, hidden, readonly.
  - Caches attributes in `DIR_INDEX_ITEM`.
- `UDFAttributesToUDF`
  - Converts NT file attributes back to UDF permissions, file type, ICB flags, and file-characteristic bits.
  - Marks file entry and directory index as modified.
- `UDFFileDirInfoToNT`
  - Fills `FILE_BOTH_DIR_INFORMATION` from a `DIR_INDEX_ITEM`.
  - Uses cached `FileInfo`/FCB state when present.
  - Reads the file entry from disk when attributes or linked state require it.
  - Converts times, sizes, attributes, long name, and DOS short name.
  - Reports zero EOF/allocation size for directories.
- `UDFSetFileXTime`
  - Writes NT times into regular or extended UDF file entries and updates directory-index cached times.
- `UDFGetFileXTime`
  - Reads UDF entry times as NT times, with fallback to current system time.
- `UDFNormalizeFileName`
  - Trims trailing nulls, trailing periods, and trailing spaces except for `.` and `..`.
- `UDFDOSNameOsNative`
  - Uses `RtlGenerate8dot3Name` to generate a DOS short name, with special handling for `.` and `..`.
- Unicode string helpers:
  - `MyAppendUnicodeStringToString_`
  - `MyAppendUnicodeToString_`
  - `MyInitUnicodeString`
  - `MyCloneUnicodeString`
  - These allocate/reallocate kernel buffers and keep strings null-terminated.
- `UDFIsDirInfoCached`
  - Checks whether all directory-index entries already have usable cached attributes and are not unresolved linked entries.
- Delete/rename policy helpers:
  - `UDFDoesOSAllowFileToBeTargetForRename__`
  - `UDFDoesOSAllowFileToBeUnlinked__`
  - `UDFDoesOSAllowFilePretendDeleted__`

## Integration Notes

This file depends on core UDFS structures and helpers such as `PVCB`, `PUDF_FILE_INFO`, `PDIR_INDEX_ITEM`, `UDFReadFileEntry`, `ValidateFileInfo`, `UDFDirIndex`, `UDFGetDirIndexByFileInfo`, cache helpers, memory wrappers, and NT runtime routines.

## Risks And Edge Cases

- `UDFTimeToUDF` computes `LocalTime` but uses `NtTime % 100` for sub-centisecond fields after conversion, which is worth verifying for precision correctness.
- Unicode append helpers reallocate manually and update `MaximumLength`; the `MyAppendUnicodeToString_` path sets `MaximumLength` based on only appended length in one branch, which may be fragile.
- `UDFFileDirInfoToNT` copies `UdfName.MaximumLength` into `FileName` while setting `FileNameLength` from `Length`; callers must ensure the output buffer is large enough.
- File deletion policy is conservative: directory targets, parentless files, stream dirs, open children, readonly attributes, and active FCB state can block operations.
- Several blocks are compiled out for `_CONSOLE` or `UDF_READ_ONLY_BUILD`, so behavior differs by build mode.
