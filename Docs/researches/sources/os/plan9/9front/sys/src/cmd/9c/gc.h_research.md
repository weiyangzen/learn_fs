# File Research: sources/os/plan9/9front/sys/src/cmd/9c/gc.h

Primary PowerPC64 backend header for `9c`.

Key contents:
- Defines target C type sizes: 32-bit `long`, 64-bit pointers/vlong/double, 8-bit char, 16-bit short, 32-bit int/float.
- Defines backend structures: `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- `Prog` supports `from`, optional third operand `from3`, destination `to`, link, source line, opcode, and register field.
- `Reg` is the optimizer CFG/liveness node with use/set bitsets, reference/call liveness, register divergence, loop weight, CFG links, and attached instruction.
- Declares extensive global compiler/backend state for code generation, switch lowering, register optimization, string/rathole handling, and variable tables.
- Defines register optimizer constants and macros for load/store bit computations.
- Declares cross-file entry points for codegen, text emission, switch/bitfield support, listing, register optimization, peephole optimization, and 64-bit helpers.
- Installs Plan 9 `#pragma varargck` contracts for custom formatters.

Filesystem relevance: indirect backend contract for the PowerPC64 compiler.
