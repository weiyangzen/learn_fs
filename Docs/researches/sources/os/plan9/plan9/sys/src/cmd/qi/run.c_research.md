# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/run.c

Instruction dispatch loop for the PowerPC interpreter.

Key responsibilities:
- Defines the primary opcode table for immediate arithmetic/logical ops, branches, syscalls, loads/stores, floating loads/stores, and group dispatch markers.
- Runs the fetch/decode/execute loop for `count` instructions.
- Dispatches primary opcodes and extended opcode groups 19, 31, 59, and 63.
- Handles overflow-enabled variants for selected opcode-31 instructions.
- Increments per-instruction counters and checks instruction breakpoints after each instruction.
- Reports illegal or not-implemented instructions via `undef()` and `unimp()`.

Dependencies:
- Uses opcode tables from `branch.c`, `iu.c`, `float.c`, and syscall handling.
- Uses `ifetch`, breakpoint checks, `power.h` register state, and longjmp error handling.

Notable risks:
- PC update convention requires instruction handlers to set `reg.pc = target - 4` for branches.
- Unsupported instruction entries with names but no function are traceable but fault when executed.
