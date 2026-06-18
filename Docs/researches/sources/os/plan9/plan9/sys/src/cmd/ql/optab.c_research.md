# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/optab.c

PowerPC instruction selection table for the linker backend.

Defines `Optab optab[]`, mapping:
- assembler opcode (`as`);
- operand classes for `from`, register, `from3`, and `to`;
- encoding type number;
- emitted instruction size;
- optional parameter register.

The table covers:
- `TEXT` pseudo-ops;
- integer moves, arithmetic, logical operations, multiply/divide/remainder;
- shifts and rotate/mask forms;
- floating-point arithmetic and moves;
- memory loads/stores for SB/SP/zero-register/long-address forms;
- branches and branch-to-LR/CTR forms;
- special registers, FPSCR, CR, MSR, SREG, SPR;
- cache/TLB/sync operations;
- FP2 and embedded PowerPC variants.

`buildop()` in `span.c` sorts this table and creates alias opcode ranges, so many related mnemonics share a base table entry.

Risk/notes:
- The numeric encoding `type` values are consumed by `asmout()` outside this group.
- Size values drive `span()` PC assignment and branch relaxation.
- Missing/incorrect operand classes surface as `illegal combination` diagnostics from `oplook()`.
