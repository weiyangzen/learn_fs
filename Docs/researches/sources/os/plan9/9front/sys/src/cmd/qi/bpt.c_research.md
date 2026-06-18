# File Research: sources/os/plan9/9front/sys/src/cmd/qi/bpt.c

Breakpoint management for the `qi` Power instruction simulator/debugger.

Key responsibilities:
- `dobplist` prints instruction, memory access, read, write, and equality breakpoints with symbol offsets.
- `breakpoint` parses breakpoint subtype suffixes and installs a `Breakpoint`.
- `delbpt` removes a breakpoint by evaluated address.
- `brkchk` checks executed/accessed addresses, handles hit counts, equality checks, and stops the run loop.

Dependencies and coupling:
- Uses `expr` for address parsing, `symoff` for display, and `getmem_4` for equality breakpoints.
- Updates global `membpt`, `count`, and `atbpt`.

Notable behavior:
- `delbpt` increments `membpt` for non-instruction breakpoint deletion; this appears counterintuitive and may be a latent bug, since add also increments it.
