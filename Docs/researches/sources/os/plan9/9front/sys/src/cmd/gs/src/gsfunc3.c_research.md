# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc3.c

## Role

`gsfunc3.c` implements several LanguageLevel 3 function types: Exponential Interpolation, 1-Input Stitching, and an internal Arrayed Output composition function.

This is PDF/PostScript function infrastructure, not filesystem code.

## Main Interfaces

- `gs_function_ElIn_init`
- `gs_function_1ItSg_init`
- `gs_function_AdOt_init`
- corresponding free-parameter functions

## Function Types

### Exponential Interpolation

Evaluates `C0 + x^N * (C1 - C0)` with optional range clipping. Initialization validates exponent/domain combinations for non-integral or negative exponents.

### 1-Input Stitching

Selects one subfunction based on input bounds, maps the input through that interval’s Encode pair, and evaluates the selected subfunction.

### Arrayed Output

Evaluates `n` subfunctions and assembles their scalar outputs into one `n`-component output. It handles overlapping input/output buffers by copying inputs to a temporary buffer when necessary.

## Scaling And Serialization

The file provides helpers to scale arrays of subfunctions and recursively serialize nested functions. Scaled copies own copied arrays/subfunctions.

## Notable Risks

- `fn_1ItSg_make_scaled` scales `pfn->params.n` functions, but the Stitching parameter’s subfunction count is `k`; this is worth reviewing if `n != k`.
- Arrayed Output uses `fn_common_get_params` with a comment questioning parameter reporting.
- Arrayed Output computes its domain as the intersection of subfunction domains, with a comment noting this is not generally correct but fits shading usage.
