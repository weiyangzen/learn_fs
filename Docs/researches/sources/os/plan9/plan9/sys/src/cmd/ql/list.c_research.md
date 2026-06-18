# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/list.c

Diagnostic and pretty-print support for the `ql` linker IR.

Main responsibilities:
- `listinit()` installs Plan 9 `Fmt` conversions for opcodes, operands, programs, symbols, and register classes.
- `prasm()` prints one `Prog`.
- `Pconv()` formats an instruction, including `ADATA`/`AINIT`/`ADYNT`, indexed addressing, `from3`, scheduling marks, and register operands.
- `Aconv()` maps opcode numbers through `anames`.
- `Dconv()` formats operand types including constants, memory references, integer/floating/control registers, SPR/DCR/FPSCR/MSR/SREG, branches, float constants, and string constants.
- `Nconv()` formats symbol-relative names for extern/static/auto/param addressing.
- `Rconv()` formats operand classes through `cnames`.
- `Sconv()` escapes fixed-width string constants.
- `diag()` reports errors against the current text symbol and exits after too many errors.

This file is not transformation logic, but it is essential for debugging all linker passes and for fatal diagnostics emitted by object loading, branch resolution, span, and instruction selection.

Risk/notes:
- `Dconv()` depends on `curp` to resolve branch target formatting.
- `diag()` increments global `nerrors`; later `errorexit()` removes partial output.
