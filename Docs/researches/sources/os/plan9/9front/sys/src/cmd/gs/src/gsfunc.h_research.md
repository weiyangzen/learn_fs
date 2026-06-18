# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc.h

## Role

`gsfunc.h` defines the abstract Ghostscript Function type, common parameter layout, procedure vector, helper macros, and generic API used by all concrete function implementations.

This is rendering/function API infrastructure, not filesystem code.

## Main Types

- `gs_function_type_t`
- `gs_function_params_t`
- `gs_function_info_t`
- `gs_function_procs_t`
- `gs_function_head_t`
- `gs_function_t`

## Procedure Vector

Concrete functions provide callbacks for:

- evaluate
- monotonicity testing
- info query
- parameter emission
- scaled-copy creation
- parameter free
- object free
- serialization

## Public Helpers

- `alloc_function_array`
- macros for `gs_function_evaluate`, `gs_function_is_monotonic`, `gs_function_get_info`, `gs_function_get_params`, `gs_function_make_scaled`, `gs_function_free_params`, `gs_function_free`, and `gs_function_serialize`

## Important Semantics

Function scaling maps outputs from `[0, 1]` into supplied target ranges and copies owned parameters/subfunctions so the new function can be freed independently. Data sources may be shared.
