# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/Sys_spec_lib.h

## Purpose

`Sys_spec_lib.h` declares the UDFS system-specific helper interface implemented by `Sys_spec_lib.cpp` and provides macros for timestamp updates, cache checks, file ID creation, allocation rounding, and device-object classification.

## Main Contents

Inside `_BROWSE_UDF_`, it declares:

- Timestamp conversion:
  - `UDFTimeToNT`
  - `UDFTimeToUDF`
- Attribute conversion:
  - `UDFAttributesToNT`
  - `UDFAttributesToUDF`
- Directory info conversion:
  - `UDFFileDirInfoToNT`
- File-entry time mutation/access:
  - `UDFSetFileXTime`
  - `UDFGetFileXTime`
- Timestamp update macros:
  - access, modify, attribute, create time updates based on VCB compatibility flags.
- Name/string helpers:
  - `UDFDOSNameOsNative`
  - `UDFNormalizeFileName`
  - `MyAppendUnicodeStringToString_`
  - `MyAppendUnicodeToString_`
  - `MyInitUnicodeString`
  - `MyCloneUnicodeString`
- Cache helpers:
  - `UDFIsDataCached`
  - `UDFIsDirInfoCached`
- File operation policy helpers:
  - rename/hardlink target checks.
  - unlink/move checks.
  - pretend-delete and OS-reference removal checks.
- Utility macros:
  - `UDFGetNTFileId`
  - `UnicodeIsPrint`
  - `UDFSysGetAllocSize`
  - `UDFIsFSDevObj`

## Integration Notes

The header is gated by `_BROWSE_UDF_`, so consumers must define that build symbol to see the main declarations. It assumes many UDFS internal types are already visible.

## Risks And Edge Cases

- Update macros evaluate arguments multiple times and embed multi-statement logic; they should be used with simple variables.
- `UDFGetNTFileId` mixes disk location, filename checksum, and VCB pointer bits, making it process/address-space dependent.
- `UDFIsDataCached` requires low IRQL and initialized write cache; callers should not assume it is purely a metadata check.
