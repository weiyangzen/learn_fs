# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc.h

## Role

Generic abstraction for Ghostscript PDF/PostScript Functions.

## Main Data

Defines `gs_function_params_common`, `gs_function_params_t`, `gs_function_info_t`, `gs_function_head_t`, procedure-vector type `gs_function_procs_t`, and base `gs_function_t`.

## Main API

Declares allocation of function arrays and macros for evaluate, monotonicity test, info, parameter writing, scaled copy creation, parameter freeing, full freeing, and serialization.

## Contract

Function type is `int` rather than enum because specific function types are declared across separate headers. Specific function implementations provide their own parameter structs, init functions, free-param functions, and GC descriptors.

## Dependencies

Uses Ghostscript ranges, data source, parameter list, stream, memory, and bool types.
