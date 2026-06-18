# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifunc.h

Defines internal interpreter APIs for PostScript/PDF Functions.

Key points:
- Includes `gsfunc.h`.
- Defines `build_function_proc` signature and function-pointer type.
- Defines `build_function_type_t`, mapping `FunctionType` integers to builder procedures.
- Declares `build_function_type_table[]` and count.
- Declares:
  - `fn_build_function`
  - `fn_build_sub_function`
  - `fn_build_float_array`
  - `fn_build_float_array_forced`
  - `ref_function`
  - `zexecfunction`
- `fn_build_float_array` handles optional/required arrays and even-length constraints.
- `fn_build_float_array_forced` also accepts a scalar numeric parameter as a one-element array.

Dependencies and interactions:
- Used by function-type operator builders and function execution operators.
- Bridges PostScript dictionary/function refs into library `gs_function_t`.

Research relevance:
- Function-object construction API for gradients, transfer functions, and PDF function semantics.
