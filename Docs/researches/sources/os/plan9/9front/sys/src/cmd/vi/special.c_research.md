# File Research: sources/os/plan9/9front/sys/src/cmd/vi/special.c

`special.c` implements MIPS SPECIAL opcode dispatch and register-register operations. The `ispec` table covers shifts, jumps, syscall, HI/LO moves, multiply/divide, add/subtract/logical operations, and set-less-than variants.

Handlers update simulator registers, HI/LO, and branch delay-slot execution. `jr`/`jalr` also support call-tree tracing with symbol/source output. `Snor()` recognizes the simulator’s chosen NOP instruction and increments `nopcount` instead of modifying registers.

This file complements `run.c` for opcode 0 instructions and shares the same stats/trace model.
