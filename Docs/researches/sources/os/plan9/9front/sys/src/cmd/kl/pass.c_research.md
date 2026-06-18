# File Research: sources/os/plan9/9front/sys/src/cmd/kl/pass.c

This file implements major middle-end linker passes for data placement, symbol validation, branch patching, and code-following.

Key functions:
- `dodata()` validates data initializers, assigns small data before larger data/BSS, inserts literal pool entries for large constants/address constants, adjusts final data/BSS offsets, and defines linker symbols `setSB`, `bdata`, `edata`, `end`, and `etext`.
- `undef()` reports unresolved `SXREF` symbols.
- `relinv()` returns inverse conditional branch opcodes for control-flow layout.
- `follow()`/`xfol()` reorder text to follow likely control flow, copy short already-followed sequences when useful, and synthesize jumps when needed.
- `patch()` resolves branch and call targets from symbol values to `Prog.cond` pointers, using `mkfwd()` skip links for faster lookup, and collapses jump chains through `brloop()`.
- `atolwhex()` parses decimal/octal/hex command arguments.
- `rnd()` aligns addresses.

The file consumes the symbol table and program list built by `obj.c` and prepares them for `span()`/`asmb()`. It assumes global linker state and Plan 9 assembler conventions.
