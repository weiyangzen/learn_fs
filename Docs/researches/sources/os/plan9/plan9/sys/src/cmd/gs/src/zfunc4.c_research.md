# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfunc4.c

PostScript/PDF support for FunctionType 4 calculator functions. PDF calculator functions use a restricted PostScript procedure language, and this file validates that subset and compiles it into Ghostscript’s `gs_PtCr_opcode_t` bytecode.

The static `calc_ops` table maps allowed arithmetic, comparison, and stack operator procedures to calculator opcodes. `check_psc_function` walks a procedure completely, accepting integer, real, boolean constants, executable `true`/`false` names, allowed executable operators, and nested procedures only when used as literal operands to `if` or `ifelse`. It enforces a maximum nesting depth of 10 and rejects unbound/unknown names or unsupported operators.

`psc_fixup` patches forward branches for `if` and `else`. `gs_build_function_4` reads the dictionary `Function` procedure, runs the validator once to compute bytecode size, allocates an opcode buffer, runs validation again to emit opcodes, appends `PtCr_return`, and calls `gs_function_PtCr_init`. Failure frees the opcode string through `gs_function_PtCr_free_params`.
