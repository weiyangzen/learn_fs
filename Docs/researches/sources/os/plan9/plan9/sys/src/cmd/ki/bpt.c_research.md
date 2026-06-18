# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/bpt.c

This file implements breakpoint management for the `ki` SPARC emulator/debugger.

`dobplist()` prints instruction, access, read, write, and equal-value breakpoints with symbolic locations. `breakpoint()` parses breakpoint type suffixes, evaluates the address expression, stores count/done values, and links the breakpoint into `bplist`.

`delbpt()` removes a breakpoint by evaluated address. `brkchk()` checks execution or memory access against the list, handles equal-value breakpoints by reading memory, decrements pass counts, and stops execution by setting `count=1` and `atbpt=1`.

Memory breakpoints increment `membpt`, causing memory access helpers to call `brkchk()`.
