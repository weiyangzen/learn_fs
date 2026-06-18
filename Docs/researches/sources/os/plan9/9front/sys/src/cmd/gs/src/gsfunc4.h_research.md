# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc4.h

## Role

`gsfunc4.h` defines FunctionType 4 PostScript Calculator function opcodes, parameters, constructor, and free routine.

This is function bytecode API infrastructure, not filesystem code.

## Main Definitions

- `function_type_PostScript_Calculator`
- `gs_PtCr_opcode_t`
- `PtCr_NUM_OPS`
- `PtCr_NUM_OPCODES`
- `gs_function_PtCr_params_t`

## Opcode Groups

- Arithmetic operators
- Comparison operators
- Stack operators
- Constants
- Special control-flow operators: `PtCr_if`, `PtCr_else`, `PtCr_return`

## Public API

- `gs_function_PtCr_init`
- `gs_function_PtCr_free_params`

## Notable Detail

The private GC descriptor macro contains a comment that it needs to include `data_source`, matching the implementation’s fabricated DataSource for symbolic output.
