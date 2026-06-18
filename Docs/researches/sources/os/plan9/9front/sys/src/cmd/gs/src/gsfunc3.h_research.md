# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc3.h

## Role

`gsfunc3.h` defines LanguageLevel 3 Ghostscript function parameter structures and constructors for Exponential Interpolation, 1-Input Stitching, and Arrayed Output functions.

This is function API infrastructure, not filesystem code.

## Main Definitions

Function type constants:

- `function_type_ExponentialInterpolation = 2`
- `function_type_1InputStitching = 3`
- `function_type_ArrayedOutput = -1`

Parameter structs:

- `gs_function_ElIn_params_t`
- `gs_function_1ItSg_params_t`
- `gs_function_AdOt_params_t`

Public functions:

- `gs_function_ElIn_init`
- `gs_function_1ItSg_init`
- `gs_function_AdOt_init`
- matching free-parameter routines

## Important Notes

Arrayed Output is internal-only and explicitly ignores Domain and Range fields.
