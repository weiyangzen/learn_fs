# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_errors.h

## Summary
Defines zstd's public error-code enum and error-string lookup declarations.

## Key APIs
- `ZSTD_ErrorCode`.
- `ZSTD_getErrorCode(size_t functionResult)`.
- `ZSTD_getErrorString(ZSTD_ErrorCode code)`.
- `ZSTDERRORLIB_API` and visibility/import/export macros.

## Important Behavior
The enum assigns stable values below 100 for core zstd errors such as prefix, frame parameter, corruption, checksum, dictionary, parameter, stage, allocation, workspace, and buffer errors. Values at and above 100 are explicitly unstable and reserved for less stable features such as frame index and seekable I/O.

The header supports C++ linkage and platform/compiler visibility attributes. It recommends using the enum names rather than relying on raw numeric values, and notes that `ZSTD_isError()` remains the robust way to detect errors across versions.

## Risks
Only the documented stable range should be used for compatibility. Dynamic linking is noted as not officially supported for this error-list API in the comments, despite DLL import/export macro support.
