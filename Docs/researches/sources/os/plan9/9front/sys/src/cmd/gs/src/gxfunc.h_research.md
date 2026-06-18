# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfunc.h

Declares internal support for Ghostscript Function objects.

Key definitions:
- Declares abstract GC structure type `st_function`.
- `public_st_function` defines GC traversal over generic function `Domain` and `Range` arrays.

Key declarations:
- `fn_common_free_params`
- `fn_common_free`
- `fn_check_mnDR`
- `gs_function_get_info_default`
- `fn_common_get_params`
- `fn_copy_values`
- `fn_scale_pairs`
- `fn_common_scale`
- `fn_common_serialize`

Dependencies:
- Includes public function API `gsfunc.h` and GC struct helpers `gsstruct.h`.

Research notes:
- Provides shared implementation helpers for concrete PostScript/PDF function types.
- Handles validation, parameter copying/scaling, serialization, and common cleanup.
