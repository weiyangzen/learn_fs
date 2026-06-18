# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc0.h

## Role

Type definitions and API for FunctionType 0 sampled functions.

## Main Data

Defines `function_type_Sampled` as `0` and `gs_function_Sd_params_t`, containing common function parameters plus order, data source, bits per sample, Encode/Decode arrays, Size array, and internal pole-cache metadata.

## Main API

Declares `gs_function_Sd_init` and `gs_function_Sd_free_params`.

## Dependencies

Includes `gsfunc.h` and `gsdsrc.h`.

## Notes

`BitsPerSample` supports 1, 2, 4, 8, 12, 16, 24, and 32. `Order` is optional and supports 1 or 3 after defaulting.
