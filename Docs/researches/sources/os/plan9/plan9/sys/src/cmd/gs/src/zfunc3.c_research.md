# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfunc3.c

PostScript interface for LanguageLevel 3 FunctionType 2 and FunctionType 3 functions. It plugs into Ghostscript’s shared function-builder path by implementing `gs_build_function_2` and `gs_build_function_3`.

`gs_build_function_2` builds Exponential Interpolation functions. It copies common Domain/Range parameters, reads required `N`, optional/defaulted `C0` and `C1`, checks output vector lengths against each other and against `Range`, then calls `gs_function_ElIn_init`. Failure paths free partially allocated function parameter arrays with `gs_function_ElIn_free_params`.

`gs_build_function_3` builds one-input stitching functions. It reads the `Functions` array, recursively builds each subfunction through `fn_build_sub_function`, requires `Bounds` length `k - 1` and `Encode` length `2 * k`, derives output count from the first subfunction when `Range` is absent, and initializes with `gs_function_1ItSg_init`. It is ownership-sensitive because the function arrays are allocated before validation completes and are released by `gs_function_1ItSg_free_params` on error.
