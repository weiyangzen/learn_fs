# File Research: sources/os/plan9/9front/sys/src/cmd/vi/run.c

`run.c` implements the main MIPS opcode table and most non-special integer/load/store/branch instructions. `run()` repeatedly zeros `r0`, fetches at `pc`, dispatches through `Iexec`, advances `pc`, checks instruction breakpoints, optionally prints register traces, and stops when `count` reaches zero.

Instruction handlers implement immediate arithmetic/logical ops, byte/half/word loads and stores, unaligned `lwl/lwr`, jumps, calls, branch and branch-likely forms with explicit delay-slot execution, `ll/sc` as uniprocessor `lw/sw`, and `bcond` variants.

The file tracks instruction counts through `Inst.count` and branch delay-slot use. Branch handlers update `pc` to `target-4` because the main loop adds 4 after dispatch.
