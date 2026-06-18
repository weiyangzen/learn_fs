# File Research: sources/windows/reactos/drivers/filesystems/udfs/mem.h

## Role

`mem.h` is the UDF driver's local memory-tool configuration header.

## Core Behavior

When `UDF_DBG` is enabled, it turns on memory-owner tracking, reference tracking, and allocation-bound checking with a two-`ULONG` guard size. It leaves optional nonpaged-only allocation and internal memory-manager modes commented out, then includes `Include/mem_tools.h`.

## Dependencies

The public allocation API comes from `Include/mem_tools.h`. Debug behavior is controlled by `UDF_DBG` and the `MY_HEAP_*` macros defined in this header before including the shared memory-tool header.

## Notable Risks

This header changes allocator instrumentation through macros, so include order matters. Production builds skip the debug heap tracking features entirely unless `UDF_DBG` is set.
