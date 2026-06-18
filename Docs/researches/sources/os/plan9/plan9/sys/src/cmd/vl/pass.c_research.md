# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/pass.c

Middle linker passes for data layout, undefined checking, code following, branch patching, and numeric parsing.

Key responsibilities:
- `dodata()` validates data initializers, lays out small data, regular data, BSS, and linker-generated literal pools.
- Converts large constants and data addresses into literal data entries when they cannot fit direct encodings.
- Defines standard linker symbols: `setR30`, `bdata`, `edata`, `end`, `etext`.
- `undef()` reports unresolved `SXREF` symbols.
- `follow()`/`xfol()` reorder control flow to favor fall-through paths and invert simple branches when profitable.
- `patch()` resolves branch/jump/return symbol targets into `Prog.cond` pointers and collapses jump chains.
- `mkfwd()` builds skip pointers for faster pc-to-`Prog` lookup.
- `atolwhex()` parses decimal, octal, and hex signed constants; `rnd()` rounds alignment.

Important behavior:
- Data symbols with zero size are diagnosed and forced to size one.
- String constants can be moved into text when debug flag `t` is set.
- Branches to undefined text symbols are redirected to `exit` after a diagnostic.

Risks:
- Layout mutates symbol types in several passes; later code relies on those exact transitions.
