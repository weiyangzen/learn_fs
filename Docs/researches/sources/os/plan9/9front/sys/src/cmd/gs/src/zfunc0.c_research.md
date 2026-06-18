# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc0.c

## Purpose
Builds FunctionType 0 sampled functions from PostScript dictionaries.

## Key Functions
- `gs_build_function_0()` fills `gs_function_Sd_params_t` from a dictionary and initializes a sampled data function.

## Important Behavior
- `DataSource` must be a string or a readable, seekable file.
- Optional `Order` defaults to 1 and is restricted to 1-3.
- `BitsPerSample` is required through `dict_int_param` default 0 and must be 1-32.
- Optional `Encode` length must be `2*m` if present; optional `Decode` length must be `2*n` if present.
- `Size` is required and must contain `m` integers.
- Failure paths call `gs_function_Sd_free_params()` before returning `rangecheck` or the underlying error.

## Research Notes
This is the direct FunctionType 0 builder used by the generic function dispatch in `zfunc.c`.
