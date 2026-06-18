# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifunc.h

Defines internal interpreter APIs for PostScript/PDF Functions.

Key points:
- Includes `gsfunc.h`.
- Defines `build_function_proc`, `build_function_proc_t`, and `build_function_type_t`.
- Declares function builder table and count.
- Declares `fn_build_function`, `fn_build_sub_function`, `fn_build_float_array`, `fn_build_float_array_forced`, `ref_function`, and `zexecfunction`.
- `fn_build_float_array` handles optional/required arrays and even-length constraints.
- `fn_build_float_array_forced` accepts scalar numeric input as a one-element array.

Research relevance:
- Function-object construction and execution API used by gradients, transfer functions, and PDF function semantics.
