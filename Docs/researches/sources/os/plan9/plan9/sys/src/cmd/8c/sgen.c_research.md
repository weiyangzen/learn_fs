# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/sgen.c

Purpose: 386 C compiler backend expression addressability and complexity analysis.

Key behavior: `xcom` recursively annotates AST nodes with `addable` classes and register complexity, folds address arithmetic, rewrites power-of-two multiply/divide/modulo into shifts/masks, and normalizes compare/immediate operands. `indexshift` and `indx` recognize x86 scaled-index forms. `noretval` emits pseudo uses for integer/FPU return registers.

Integration notes: feeds code generation in `txt.c`/`cgen.c`; its `addable` values are consumed by `naddr`, `gins`, and indexed addressing setup. Important edge cases are side-effect avoidance before forming `OINDEX`, 64-bit expression handling via `com64`, and register-pressure estimates for calls and division.
