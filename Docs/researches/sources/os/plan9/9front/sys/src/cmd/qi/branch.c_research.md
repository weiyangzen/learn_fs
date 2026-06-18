# File Research: sources/os/plan9/9front/sys/src/cmd/qi/branch.c

Power branch and condition-register instruction handlers for `qi`.

Key responsibilities:
- Defines extended opcode group 19 table `op19`.
- `condok` evaluates branch condition fields and count-register behavior.
- `dobranch`, `bcctr`, `bclr`, `bcx`, and `bx` implement conditional/unconditional branches, link-register updates, and trace strings.
- `crop` implements condition-register boolean operations.
- `mcrf` moves condition-register fields.
- `call` and `ret` support optional call-tree tracing using symbols and stack parameter printing.
- `isync` is treated as a traced no-op.

Dependencies and coupling:
- Uses `reg` state, `bits[]`, `ci->taken`, `undef`, symbol functions, and command tracing globals.
- Hooks into `run.c` opcode dispatch through `ops19`.

Notable behavior:
- Branch handlers set `reg.pc = target - 4`; the run loop increments PC after each instruction.
