# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/physical.cpp

## Purpose

`physical.cpp` is a thin compile-unit wrapper for physical device read/write support. It includes `udf.h`, defines this unit's `UDF_BUG_CHECK_ID` as `UDF_FILE_PHYSICAL`, then directly includes `Include/phys_lib.cpp`.

## Behavior

There are no local functions or data structures in this file beyond the bug-check identifier. The actual physical I/O implementation is pulled in textually from `sources/windows/reactos/drivers/filesystems/udfs/udf_info/Include/phys_lib.cpp`.

## Dependencies

- `udf.h` provides the UDFS platform and internal declarations required by the included physical I/O library.
- `Include/phys_lib.cpp` owns the substantive implementation compiled as part of this translation unit.

## Notes

Because this file uses a `.cpp` include rather than linking a separately compiled object, `UDF_BUG_CHECK_ID` and any local preprocessor context apply to the included physical I/O code.
