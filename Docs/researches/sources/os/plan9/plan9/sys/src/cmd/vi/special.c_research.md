# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/special.c

Purpose: Implements MIPS SPECIAL opcode instructions.

Key behavior:
- Defines the secondary function dispatch table.
- Implements shifts, logical ops, set-less-than, add/sub variants, jumps through registers, syscall dispatch, HI/LO moves, multiply, and divide.
- Handles delay slots for `jr` and `jalr`.
- Treats `nor r0,r0,r0` as the simulator’s nop marker and counts nops.

Dependencies:
- Uses multiply helpers from `vi.c`, syscall handler, register state, tracing, source/call-tree helpers, and decode macros.

Notable details:
- Some instruction handlers decode destination register with masks wider than 5 bits, but operands originate from MIPS instruction fields.
