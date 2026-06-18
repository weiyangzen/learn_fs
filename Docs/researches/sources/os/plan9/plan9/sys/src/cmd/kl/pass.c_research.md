# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/pass.c

Read fully: 551 lines, 9340 bytes. SHA-256 prefix: `99e4622eb545f572`.

This file implements middle linker passes for data layout, undefined-symbol checks, branch inversion, control-flow following, branch patching, and numeric parsing/alignment.

Key behavior:
- `dodata()` validates data initializers, lays out small data first, then large data, then BSS; creates literal data symbols for large constants or symbolic addresses; defines `setSB`, `bdata`, `edata`, `end`, and `etext`.
- `undef()` reports remaining unresolved xrefs.
- `relinv()` returns inverse conditional branches where safe.
- `follow()`/`xfol()` reorder code into a followed control-flow order, cloning short sequences when useful and inserting jumps where needed.
- `patch()` resolves branch and call targets, converts symbolic calls to `D_BRANCH`, builds forward pointers with `mkfwd()`, and collapses branch chains with `brloop()`.
- `atolwhex()` parses decimal, octal, and hex with sign handling.
- `rnd()` aligns values.

Integration: runs after object loading and before no-op/prologue expansion. It establishes symbol addresses and branch `cond` pointers consumed by `noops()`, `span()`, and `asmout()`.

Risk notes: `dodata()` mutates constants into literal memory references. `xfol()` clones instructions in followed blocks and relies on mark flags to avoid infinite traversal.
