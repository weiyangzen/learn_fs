# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/gc.h

## Purpose
Main backend header for the Plan 9 386 C compiler.

## Key Definitions
- Machine sizes: `SZ_CHAR`, `SZ_SHORT`, `SZ_INT`, `SZ_LONG`, `SZ_IND`, `SZ_FLOAT`, `SZ_VLONG`, `SZ_DOUBLE`.
- Backend structures:
  - `Adr`: abstract assembly operand.
  - `Prog`: abstract assembly instruction.
  - `Case` / `C1`: switch lowering records.
  - `Var`: optimizable variable descriptor.
  - `Reg`: control-flow/data-flow graph node.
  - `Rgn`: register-allocation live region.
  - `Renv`: register environment.
- Global backend state for programs, registers, variables, flow graph, region allocator, temporaries, string data, safe temporaries, and debug state.

## Important Interfaces
Declares functions from:
- `sgen.c` for statement generation,
- `cgen.c` and `cgen64.c` for expression lowering,
- `txt.c` for instruction emission/register allocation,
- `swt.c` for switches/bitfields/data output,
- `list.c` for formatting,
- `reg.c` and `peep.c` for optimization,
- `div.c` and `mul.c` for arithmetic strength reduction.

## Research Notes
This header is the shared backend contract tying parsing/IR from `cc` to 386-specific code generation and optimization.
