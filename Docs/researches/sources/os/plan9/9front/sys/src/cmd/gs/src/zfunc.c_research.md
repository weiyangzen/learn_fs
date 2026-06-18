# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc.c

## Purpose
Implements the generic PostScript interface to PDF/PostScript functions: building function structures, wrapping them as executable closures, executing them, and recognizing encapsulated functions.

## Key Functions
- `make_function_proc()` creates an executable two-element closure containing the function struct and `%execfunction`.
- `zbuildfunction()` builds a function from a dictionary and replaces the operand with the closure.
- `zexecfunction()` reads function inputs from the operand stack, evaluates the function, and writes outputs back.
- `zisencapfunction()` tests whether a procedure is a Ghostscript function closure.
- `fn_build_function()` and `fn_build_sub_function()` dispatch by `FunctionType` using `build_function_type_table`.
- `fn_build_float_array()` reads required/optional float arrays and validates even element counts when requested.
- `fn_build_float_array_forced()` accepts either an array or a scalar numeric parameter.
- `ref_function()` recognizes closures produced by `.buildfunction`.

## Important Behavior
- Nested subsidiary functions are limited by `MAX_SUB_FUNCTION_DEPTH` (3).
- Common `Domain` and optional `Range` are collected before dispatching to type-specific builders.
- `%execfunction` uses a stack buffer for small input/output counts and heap allocation for larger functions.
- Closure arrays are execute-only/executable and include an internal operator not normally defined in `systemdict`.

## Research Notes
Type-specific builders are registered elsewhere, including FunctionType 0 support in `zfunc0.c` and sampled-procedure conversion in `zfsample.c`.
