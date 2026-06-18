# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc4.c

## Purpose
Builds PDF/PostScript FunctionType 4 calculator functions by validating a restricted PostScript procedure and encoding it into Ghostscript calculator bytecode.

## Key Functions
- `check_psc_function()` walks a procedure, validates literals/operators/control forms, and optionally emits opcodes.
- `psc_fixup()` patches branch offsets for `if` and `ifelse`.
- `gs_build_function_4()` validates, allocates, encodes, terminates, and initializes a calculator function.

## Important Behavior
- Accepts only numeric, boolean, procedure constants in control positions, `true`/`false`, and a fixed whitelist of operators.
- Name operands must resolve to executable systemdict operators and match the calculator opcode table.
- Recursion is capped at 10 nested procedures.
- The builder does a sizing pass before allocating the encoded operation string.

## Research Notes
This file is a compiler from a constrained PostScript subset to an internal function VM used by PDF shading/functions.
