# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/string_lib.cpp

## Purpose
Supplies small RTL/string compatibility functions for non-native or user-mode builds.

## Main Responsibilities
- `MyRtlCompareMemory` returns the count of equal bytes from two buffers.
- Non-`NT_NATIVE_MODE` provides `RtlCompareUnicodeString`, `RtlUpcaseUnicodeString`, and `RtlAppendUnicodeToString`.
- `CDRW_W32` provides `MyInitUnicodeString` to allocate and initialize a `UNICODE_STRING`.

## Implementation Notes
- Uses x86 inline assembly for some wide-string length scans when `_X86_` is set, otherwise C loops.
- `RtlAppendUnicodeToString` can grow the destination buffer with `ExAllocatePoolWithTag` and frees the old buffer with `ExFreePool`.
- Case-insensitive comparison is not actually implemented in `RtlCompareUnicodeString`; `UpCase` is ignored.

## Notable Risks
This is compatibility glue, not a complete RTL implementation. Callers expecting exact NT semantics may get simplified behavior.
