# File Research: sources/os/plan9/9front/sys/src/cmd/kc/list.c

Formatting support for SPARC compiler backend diagnostics and debug dumps. `listinit` installs Plan 9 `Fmt` converters for instructions, opcodes, addresses, string constants, symbolic names, and bitsets. `Pconv` renders `Prog` instructions with special formatting for `ADATA` and `ATEXT`; `Dconv` and `Nconv` print address modes and symbolic offsets.

`Bconv` prints variable bitsets using the global `var[]` table. `Sconv` escapes fixed-width string constants using Plan 9-style escapes. This file has no code-generation logic, but is essential for readable debug output under backend debug flags.
