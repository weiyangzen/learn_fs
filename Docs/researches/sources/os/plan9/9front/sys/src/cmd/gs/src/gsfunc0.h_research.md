# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc0.h

## Role

`gsfunc0.h` defines FunctionType 0 Sampled function parameters and public constructor/free functions.

This is sampled-function API infrastructure, not filesystem code.

## Main Definitions

- `function_type_Sampled`
- `gs_function_Sd_params_t`
- `private_st_function_Sd`
- `gs_function_Sd_init`
- `gs_function_Sd_free_params`

## Parameter Fields

`gs_function_Sd_params_t` includes common function fields plus:

- `Order`
- `DataSource`
- `BitsPerSample`
- `Encode`
- `Decode`
- `Size`
- internal cache fields: `pole`, `array_step`, `stream_step`, `array_size`

## Important Contract

Although the struct exposes internal cache fields, callers are expected to provide the external sampled-function parameters and let initialization manage internal cache setup.
