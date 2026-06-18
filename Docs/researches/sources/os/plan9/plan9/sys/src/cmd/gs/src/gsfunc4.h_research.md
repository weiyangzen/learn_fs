# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc4.h

## Role

Public definitions for FunctionType 4 PostScript Calculator functions.

## Main Data

Defines `function_type_PostScript_Calculator` as `4`, the calculator opcode enum, opcode count macros, and `gs_function_PtCr_params_t` with common function parameters plus an opcode byte string.

## Main API

Declares `gs_function_PtCr_init` and `gs_function_PtCr_free_params`.

## Dependencies

Includes `gsfunc.h`.

## Notes

Opcodes include arithmetic, comparison, stack operators, constants, and special control operators `if`, `else`, and `return`. The ops string is represented as `gs_const_string`.
