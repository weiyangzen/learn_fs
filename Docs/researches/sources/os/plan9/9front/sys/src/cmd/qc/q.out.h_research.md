# File Research: sources/os/plan9/9front/sys/src/cmd/qc/q.out.h

Power object-code ABI header for assembler/compiler/linker coordination.

Key contents:
- Symbol/register constants: `NSNAME`, `NSYM`, `NREG`, text flags `NOPROF`, `DUPOK`.
- Register numbering conventions for general and floating registers, return registers, argument register, compiler temporaries, register variables, external registers, and fixed float constants.
- Full `enum as` opcode list for Power instructions, Plan 9 pseudo-ops, embedded PowerPC instructions, optional 32-bit instructions, and secondary/parallel floating-point opcodes.
- Address/name kinds such as `D_EXTERN`, `D_STATIC`, `D_AUTO`, `D_PARAM`, `D_BRANCH`, `D_OREG`, `D_CONST`, `D_REG`, `D_FREG`, `D_SPR`, `D_FILE`, `D_DCR`.
- `Ieee` serialized floating-constant representation.

Dependencies and coupling:
- Included by `gc.h` and shared with the Power assembler/linker object stream.
- `qa/lex.c` opcode table and `qc/txt.c` instruction selection both depend on these enumerators.

Filesystem/OS relevance:
- Defines the binary object format vocabulary used for Plan 9 Power object files.
