# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfunc0.c

## Purpose
Builds FunctionType 0 sampled functions from PostScript dictionaries.

## Key Functions
- `gs_build_function_0()` fills `gs_function_Sd_params_t` from a dictionary and initializes a sampled data function.

## Important Behavior
- `DataSource` must be a string or a readable, seekable file.
- Optional `Order` defaults to 1 and is restricted to 1-3.
- `BitsPerSample` must be 1-32.
- Optional `Encode` length must be `2*m`; optional `Decode` length must be `2*n`.
- `Size` is required and must contain `m` integers.
- Failure paths call `gs_function_Sd_free_params()`.

## Research Notes
Direct FunctionType 0 builder used by generic function dispatch in `zfunc.c`.
