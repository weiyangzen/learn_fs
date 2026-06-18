# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc.c

## Role

`gsfunc.c` implements generic Ghostscript Function support shared by PDF/PostScript function types.

This is rendering/function infrastructure, not filesystem code.

## Main Interfaces

- `alloc_function_array`
- `fn_common_free_params`
- `fn_common_free`
- `fn_check_mnDR`
- `gs_function_get_info_default`
- `fn_common_get_params`
- `fn_copy_values`
- `fn_scale_pairs`
- `fn_common_scale`
- `fn_common_serialize`

## Core Behavior

The file provides allocation, validation, copying, scaling, parameter emission, and serialization helpers for concrete function types.

Validation checks:

- positive input/output counts
- ordered `Domain` pairs
- ordered `Range` pairs when present

Scaling helpers copy generic `Domain`/`Range` arrays and optionally map output range pairs through supplied target ranges.

## Notable Risks

- `fn_common_serialize` only supports missing `Range` with a small fixed dummy array; larger missing ranges return `unregistered`.
- Data sources are shared, not copied, by scaled functions according to the generic API contract.
