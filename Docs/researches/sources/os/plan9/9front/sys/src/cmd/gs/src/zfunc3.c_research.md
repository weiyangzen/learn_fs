# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc3.c

## Purpose
Builds Ghostscript LanguageLevel 3 FunctionType 2 and FunctionType 3 PostScript functions from dictionaries.

## Key Functions
- `gs_build_function_2()` builds exponential interpolation functions from `N`, optional `C0`, optional `C1`, and inherited Domain/Range parameters.
- `gs_build_function_3()` builds one-input stitching functions from `Functions`, `Bounds`, and `Encode`.

## Important Behavior
- FunctionType 2 defaults `C0` and `C1` to one-element arrays when absent and verifies output dimensions match Range.
- FunctionType 3 recursively builds subfunctions and requires `Bounds` length `k - 1` and `Encode` length `2 * k`.
- Both builders clean up allocated parameter storage on failure.

## Research Notes
Interpreter glue around the Ghostscript function library; no direct filesystem logic.
