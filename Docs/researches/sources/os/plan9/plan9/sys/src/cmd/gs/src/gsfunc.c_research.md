# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc.c

## Role

Generic support code shared by Ghostscript function implementations.

## Main Data

Defines GC descriptors for `gs_function_t`, function pointer arrays, and function pointer array elements.

## Control Flow

Provides allocation of initialized function arrays, common parameter freeing, common function freeing, validation of input/output counts plus Domain/Range order, default info population, common parameter writing, copying numeric arrays, range-scaling Domain/Range pairs, generic function scaling setup, and serialization of common function fields.

## Dependencies

Uses `gxfunc.h`, `gsparam.h`, Ghostscript memory/error APIs, and `stream`.

## Notes

`fn_common_serialize` writes a dummy zero Range when no Range exists, but only supports up to eight dummy values; larger no-Range functions return `unregistered`.
