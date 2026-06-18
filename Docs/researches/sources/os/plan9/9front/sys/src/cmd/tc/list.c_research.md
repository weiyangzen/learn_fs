# File Research: sources/os/plan9/9front/sys/src/cmd/tc/list.c

Provides formatting routines for debug/listing output from the Thumb compiler backend.

Key points:
- `listinit` installs custom formatters for opcodes, programs, strings, names, bitsets, addresses, and register lists.
- `Bconv` prints compiler bitsets as variable names or constant offsets.
- `Pconv` formats `Prog` instructions, including special cases for `MOVM` and `DATA`.
- `Aconv` maps opcode numbers through `anames`.
- `Dconv` formats all backend address kinds: extern/static/name, const, offset register, register, float register, PSR, branch, floating constant, and string constant.
- `Rconv` formats `MOVM` register-list constants.
- `Sconv` escapes fixed-size string constants.
- `Nconv` formats symbolic address names relative to `SB`, `SP`, or `FP`.

Dependencies and interactions:
- Uses `Fmt`, `Adr`, `Prog`, `Var`, symbol tables, and opcode names from `gc.h`.
- Called by debug printing in codegen, register allocation, and object emission.

Research relevance:
- This file makes backend diagnostics and listings readable.
