# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc3.h

## Role

Declarations for LL3 function types.

## Main Data

Defines function type values for exponential interpolation (`2`), 1-input stitching (`3`), and internal arrayed output (`-1`). Declares parameter structs for `gs_function_ElIn_params_t`, `gs_function_1ItSg_params_t`, and `gs_function_AdOt_params_t`.

## Main API

Declares init and free-param functions for each type.

## Dependencies

Includes `gsfunc.h` and `gsdsrc.h`; uses Ghostscript memory and function pointer types.

## Notes

Arrayed-output functions intentionally ignore Domain and Range in their parameter description and are used to combine multiple one-output functions into one multi-output function.
