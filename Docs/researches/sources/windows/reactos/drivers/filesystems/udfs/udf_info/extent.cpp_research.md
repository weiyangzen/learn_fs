# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/extent.cpp

## Purpose
Implements UDF extent and allocation mapping management for the ReactOS UDFS driver. It converts on-disk allocation descriptors into internal `EXTENT_MAP` arrays, translates file offsets to LBAs, resizes extents, builds allocation descriptor streams for writes, handles sparse/not-recorded extent state transitions, and performs extent-backed read/write/zero operations.

## Key Elements
- `UDFExtentOffsetToLba`, `UDFNextExtentToLba`, `UDFGetExtentLength`, `UDFGetMappingLength`, and `UDFMergeMappings` provide core extent traversal, length accounting, and array manipulation.
- `UDFShortAllocDescToMapping`, `UDFLongAllocDescToMapping`, and `UDFExtAllocDescToMapping` parse short, long, and extended allocation descriptors, including recursive `EXTENT_NEXT_EXTENT_ALLOCDESC` chains.
- `UDFReadMappingFromXEntry` chooses the allocation descriptor format from file-entry/extended-file-entry ICB flags and handles `ICB_FLAG_AD_IN_ICB` by returning an in-entry offset rather than a mapping.
- Write builds are guarded by `#ifndef UDF_READ_ONLY_BUILD`; they include short/long descriptor serialization, optional fragmented allocation descriptor chains, FE-space preallocation, allocation caches, file-allocation cleanup, resize, write, and zero/deallocate paths.
- `UDFResizeExtent` is the main grow/shrink engine. It can grow sparse extents, extend the last physical fragment when adjacent free space exists, allocate new fragments, cache truncated preallocated tails, and normalize in-ICB transitions.
- `UDFMarkAllocatedAsRecorded`, `UDFMarkNotAllocatedAsAllocated`, and `UDFMarkAllocatedAsNotXXX` split and rewrite mapping arrays as data moves between recorded, allocated-not-recorded, and not-allocated-not-recorded states.
- `UDFPackMapping` merges adjacent compatible fragments; `UDFUnPackMapping` expands mappings to one logical block per entry for FE-charge allocation.
- `UDFReadExtent`, `UDFReadExtentLocation`, `UDFIsExtentCached`, `UDFWriteExtent`, and `UDFZeroExtent` bridge extent mappings to the lower block-cache/data I/O layer.

## Dependencies
Uses UDF structures and constants from `udf.h`/ECMA definitions, pool helpers (`MyAllocatePoolTag__`, `MyReallocPool__`, `MyFreePool__`), bitmap/allocation helpers (`UDFAllocFreeExtent`, `UDFMarkSpaceAsXXX`, `UDFCheckSpaceAllocation`), cache helpers (`WCache*`, `UDFIsDataCached`), and physical/logical partition translation helpers (`UDFPartLbaToPhys`, `UDFPhysLbaToPart`, `UDFPartStart`, `UDFPartEnd`).

## Behavior/Risks
This is high-risk write-path code: it mutates allocation bitmaps and extent arrays while preserving UDF extent flags in the upper bits of `extLength`. Alignment is frequently rounded to logical block size and several compatibility paths exist for Windows 2000 and Adaptec DirectCD media. Recursive allocation descriptor parsing is bounded by `ALLOC_DESC_MAX_RECURSE`.

Potential concerns include heavy manual memory ownership, many conditional build paths, several “must never happen” realloc assumptions on truncate, disabled/commented code for extended allocation descriptor building, and a suspicious `UDFLocateLbaInExtent` range predicate that appears inverted for locating an LBA within `[extLocation, extLocation + length)`. Sparse support depends on `ALLOW_SPARSE`; otherwise paths deliberately hit `BrutePoint`.
