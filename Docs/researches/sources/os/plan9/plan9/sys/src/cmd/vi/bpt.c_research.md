# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/bpt.c

Purpose: Breakpoint management for the Plan 9 MIPS interpreter/debugger.

Key behavior:
- Lists instruction, access, read, write, and equal-value breakpoints.
- Adds breakpoints with type suffixes, resolving addresses through the command expression parser.
- Deletes breakpoints by address.
- `brkchk` tests breakpoints on instruction/memory events and stops execution by setting `count` and `atbpt`.

Dependencies:
- Uses debugger globals, `symoff`, memory access helpers, and command parsing from `cmd.c`.

Notable details:
- In `delbpt`, deleting a non-instruction breakpoint increments `membpt`; this looks counterintuitive because adding one also increments it.
