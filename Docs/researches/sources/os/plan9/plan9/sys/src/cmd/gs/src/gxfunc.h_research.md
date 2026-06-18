# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfunc.h

## Purpose
Declares internal helpers for Ghostscript Function objects.

## Main GC Definition
Declares `st_function` and `public_st_function`, marking the generic function type with two pointer fields:
- `params.Domain`
- `params.Range`

## Declared Helpers
- `fn_common_free_params`
- `fn_common_free`
- `fn_check_mnDR`
- `gs_function_get_info_default`
- `fn_common_get_params`
- `fn_copy_values`
- `fn_scale_pairs`
- `fn_common_scale`
- `fn_common_serialize`

## Responsibilities
The helpers cover common Function lifecycle, validation, parameter export, value copying, range/decode scaling, and serialization behavior.

## Integration
Used by concrete PostScript/PDF function implementations. Depends on `gsfunc.h` and Ghostscript structure/GC macros.
