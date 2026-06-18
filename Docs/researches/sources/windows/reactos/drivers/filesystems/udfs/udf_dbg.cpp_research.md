# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_dbg.cpp

## Purpose

`udf_dbg.cpp` implements debug-only support helpers for resource acquisition tracing, reference counter tracing, pool allocation tracking, and guarded wait helpers. It is compiled when `UDF_DBG` or `PRINT_ALWAYS` is defined.

## Resource Debug Wrappers

The file wraps ERESOURCE operations with optional diagnostics:

- `UDFDebugAcquireResourceSharedLite()`
- `UDFDebugAcquireSharedStarveExclusive()`
- `UDFDebugAcquireResourceExclusiveLite()`
- `UDFDebugReleaseResourceForThreadLite()`
- `UDFDebugDeleteResource()`
- `UDFDebugInitializeResourceLite()`
- `UDFDebugConvertExclusiveToSharedLite()`
- `UDFDebugAcquireSharedWaitForExclusive()`

These assert IRQL below `DISPATCH_LEVEL`, optionally print resource/thread/bug-check/line information under `TRACK_RESOURCES`, and maintain `ResCounter` / `AcqCounter`. When `USE_DLD` is enabled, blocking acquisitions are routed through deadlock-detector hooks.

## Reference Counter Debugging

- `UDFDebugInterlockedIncrement()`
- `UDFDebugInterlockedDecrement()`
- `UDFDebugInterlockedExchangeAdd()`

With `TRACK_REF_COUNTERS`, these print thread, source ID, source line, target address, and before/after values. Otherwise they directly call the normal interlocked primitive.

## Pool Tracking

When tracking is enabled, the file uses a static `MemDesc` array of 8192 descriptors:

- `DebugAllocatePool()` records address, requested length, pool type, and optionally source ID/line.
- `DebugFreePool()` finds the descriptor, updates paged/nonpaged byte counters, clears the descriptor, and frees the block.
- `AllocCountPaged`, `AllocCountNPaged`, and `cur_max` summarize tracked state.

If the descriptor table fills, allocations still proceed but are not fully tracked.

## Wait Helpers

- `UDFWaitForSingleObject()` is a simple polling wait over a `LONG` signal variable with delay intervals.
- `DbgWaitForSingleObject_()` repeatedly waits on a kernel object with a bounded timeout slice, printing “No response ?” on repeated timeouts and breaking into the debugger near the end.

## Integration

The matching macros and declarations live in `udf_dbg.h`. In debug builds, driver code can route synchronization and memory allocation through these wrappers using macros that attach bug-check ID and source line information.

## Notable Risks

- The static memory descriptor table is global and not visibly synchronized in this file.
- `UDFWaitForSingleObject()` returns `STATUS_SUCCESS` even if its polling loop exits after timeout without the signal becoming true.
- Resource tracing counters are diagnostic only; they are not enforcement mechanisms.
