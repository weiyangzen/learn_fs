# File Research: sources/os/plan9/9front/sys/src/cmd/vi/bpt.c

`bpt.c` implements breakpoints for the `vi` MIPS simulator/debugger. It supports instruction breakpoints plus memory read, write, access, and equality breakpoints, each with a count/repeat value.

`breakpoint()` parses breakpoint modifiers, stores the expression-derived address, and links a new `Breakpoint`. `delbpt()` removes by address. `brkchk()` is called during instruction and memory access paths to stop execution by setting `count=1` and `atbpt=1`.

`dobplist()` formats active breakpoints with symbol offsets for debugger display.
