# File Research: sources/os/plan9/9front/sys/src/cmd/qi/run.c

Instruction dispatch loop for `qi`.

Key responsibilities:
- Defines primary opcode table `op0`.
- Dispatches instruction groups 19, 31, 59, and 63 to their extended opcode tables.
- Handles OE variants in group 31 through `oemflag`.
- `run` fetches, decodes, counts, executes, advances PC, and checks instruction breakpoints until `count` expires.
- `undef` and `unimp` report illegal/unimplemented instruction faults and return to the debugger via `longjmp`.

Dependencies and coupling:
- Uses `ifetch`, `reg`, `ci`, opcode tables from other modules, and breakpoint logic.
- Relies on instruction handlers to set `reg.pc = target - 4` for branches.

Notable behavior:
- Group 63 has two decode paths: arithmetic subset by low XO bits first, then full XO FPSCR/unary table.
