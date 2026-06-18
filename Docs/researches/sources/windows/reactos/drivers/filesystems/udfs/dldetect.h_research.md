# File Research: sources/windows/reactos/drivers/filesystems/udfs/dldetect.h

## Purpose

`dldetect.h` declares the UDFS deadlock detector API and the small tracking structures used by `dldetect.cpp`. It is intended for NT kernel-mode debug/resource-acquisition instrumentation.

## Public API

- `DLDInit(ULONG MaxThrdCount)`: initialize the detector with a maximum number of tracked threads.
- `DLDAcquireExclusive(PERESOURCE Resource, ULONG BugCheckId, ULONG Line)`: acquire an ERESOURCE exclusively with deadlock tracking.
- `DLDAcquireShared(PERESOURCE Resource, ULONG BugCheckId, ULONG Line, BOOLEAN WaitForExclusive)`: acquire shared with deadlock tracking.
- `DLDAcquireSharedStarveExclusive(PERESOURCE Resource, ULONG BugCheckId, ULONG Line)`: declared but not implemented in the paired source file.
- `DLDUnblock(PERESOURCE Resource)`: declared but not implemented in the paired source file.
- `DLDFree()`: free detector state.

## Macros and Constants

- `DLDAllocatePool(size)` and `DLDFreePool(addr)` wrap UDFS pool allocation helpers using nonpaged pool.
- `DLDGetCurrentResourceThread()` casts `PsGetCurrentThread()` to `ERESOURCE_THREAD`.
- `ResourceOwnedExclusive` is defined as `0x80` if absent.
- `ResourceDisableBoost` is defined as `0x08`.

## Structures

- `THREAD_STRUCT`: stores a tracked thread id, the resource it is currently waiting on, and the bug-check id/source line for the acquisition point.
- `THREAD_REC_BLOCK`: stores a thread plus the resource it holds while reporting or walking a wait chain.

## Integration Points

The declarations are consumed by debug wrappers in `udf_dbg.cpp` and initialization in `udfinit.cpp`. The detector source depends on these structures and macros exactly.

## Notable Risks

The header exposes APIs that model old `ERESOURCE` internals rather than opaque resource APIs. The two unimplemented declarations should be checked before enabling code paths that call them. The memory macros assume UDFS allocation helpers are available through `udffs.h` or prior includes.
