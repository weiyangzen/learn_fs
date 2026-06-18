# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_dbg.h

## Purpose

`udf_dbg.h` defines the UDFS debug/trace macro layer used across the driver. It controls print routing, breakpoint behavior, protected memory wrappers, debug pool allocation, structure validation, and hex dumping.

## Main Controls

The header exposes compile-time switches such as:

- `UDF_DBG`
- `PRINT_ALWAYS`
- `TRACK_SYS_ALLOCS`
- `TRACK_SYS_ALLOC_CALLERS`
- `USE_DLD`
- `PROTECTED_MEM_RTL`
- `USE_KD_PRINT`
- `USE_MM_PRINT`
- `USE_AD_PRINT`
- `UDF_DUMP_EXTENT`
- `ALWAYS_CHECK_WAIT_TIMEOUT`
- `CHECK_REF_COUNTS`
- `VALIDATE_STRUCTURES`

## Print Macros

When debug printing is enabled:

- `KdPrint`, `MmPrint`, `TmPrint`, `PerfPrint`, `AdPrint`, `ThPrint`, and `ExtPrint` map to `DbgPrint` variants depending on feature macros.
- `AdPrint` and `ThPrint` include the current thread.
- Without debug/always-print, most macros compile to no-ops.

## Allocation And Memory Helpers

- Under `TRACK_SYS_ALLOCS`, `DbgAllocatePool`, `DbgAllocatePoolWithTag`, and `DbgFreePool` route to `DebugAllocatePool()` / `DebugFreePool()`.
- Otherwise they map directly to `ExAllocatePoolWithTag()` / `ExFreePool()`.
- Under `PROTECTED_MEM_RTL`, `DbgMoveMemory`, `DbgCopyMemory`, and `DbgCompareMemory` wrap RTL memory operations in SEH and break on exceptions.

## Breakpoint And Validation

- `UDFBreakPoint()` maps to `int 3` on x86 debug builds or `DbgBreakPoint()` elsewhere.
- `BrutePoint()` breaks only when `BRUTE` is defined.
- `ASSERT_REF()` is controlled by `CHECK_REF_COUNTS`.
- `ValidateFileInfo()` can detect deallocated or malformed `FileInfo` structures when `VALIDATE_STRUCTURES` is enabled.
- `UDFTouch()` forces a read from an address, using x86 inline assembly when available.

## Dumping

`KdDump(a,b)` hex-dumps a memory region when debug output is enabled and becomes a no-op otherwise. `UserPrint` aliases `KdPrint`.

## Integration

This header is included broadly by UDFS driver code and provides the debug abstraction layer used by `udf_dbg.cpp`, `secursup.cpp`, directory parsing, allocation diagnostics, and many support modules.

## Notable Details

- Retail/non-debug builds keep allocation and memory macros direct and remove most diagnostics.
- The protected memory macros intentionally swallow exceptions after breaking, which is useful for diagnostics but can hide the exact failing instruction flow in normal control logic.
