# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc4.c

## Role

`gsfunc4.c` implements FunctionType 4 PostScript Calculator functions as a compact bytecode interpreter.

This is PDF/PostScript function evaluation infrastructure, not filesystem code.

## Main Interface

- `gs_function_PtCr_init`
- `gs_function_PtCr_free_params`

## Core Behavior

The evaluator uses a stack of typed values:

- bool
- int
- float

It interprets bytecode opcodes for:

- arithmetic
- trigonometric/math functions
- integer bit operations
- comparisons
- stack manipulation
- constants
- conditional `if`/`else`
- `return`

A dispatch table maps opcode plus operand types to either a typed opcode, a coercion opcode, a no-op, or typecheck.

## Additional Support

- `calc_put_ops` reconstructs a symbolic PostScript-like function body.
- `calc_access` exposes that symbolic body through a fabricated `DataSource`, using a SubFileDecode filter to extract requested substrings.
- `fn_PtCr_make_scaled` appends scaling bytecode to transform outputs into target ranges.
- `gs_function_PtCr_init` prevalidates bytecode structure and final `return`.

## Notable Risks

- Monotonicity is not analyzed; it returns unknown/non-monotonic mask.
- Stack depth is limited to 100.
- `calc_access` is intentionally inefficient and described as rarely used.
- The header notes the GC descriptor needs to include the bogus `data_source`; current descriptor only adds `params.ops`.
