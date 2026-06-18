# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/list.c

This file installs and implements Plan 9 fmt conversions for SPARC compiler backend diagnostics and listings.

`listinit()` registers `%A`, `%P`, `%S`, `%N`, `%D`, and `%B`. `Pconv()` formats full instructions with special handling for `DATA` and `TEXT`. `Aconv()` maps opcodes through `anames[]`.

`Dconv()` formats addresses by operand type, including constants, memory references, registers, branches, floating constants, and string constants. `Nconv()` formats symbol-relative names as SB/SP/FP forms. `Sconv()` escapes fixed-size string constants.

The file is non-semantic but essential for debugging generated code, register allocation, and compiler diagnostics.
