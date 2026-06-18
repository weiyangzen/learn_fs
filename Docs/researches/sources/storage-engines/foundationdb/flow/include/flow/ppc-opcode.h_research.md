# sources/storage-engines/foundationdb/flow/include/flow/ppc-opcode.h

## Purpose
Defines raw PowerPC VSX/crypto opcode encodings for assemblers lacking selected instruction mnemonics.

## Important APIs, Types, And Functions
Field helpers include `__PPC_RA`, `__PPC_RB`, `__PPC_XA`, `__PPC_XB`, `__PPC_XS`, and `__PPC_XT`. `VSX_XX3` and `VSX_XX1` assemble operands. Instruction constants cover `VPMSUMW`, `VPMSUMD`, `MFVSRD`, and `MTVSRD`; macros emit `.long` words.

## Control Flow
Assembly expands these macros into numeric instruction words. There is no runtime C++ behavior.

## State And Persistence Behavior
No state. The macros affect emitted machine code.

## Dependencies And Integration Points
Pairs with PowerPC assembly, often accelerated checksum/CRC implementations, and with `ppc-asm.h` register/function macros.

## Risks And Edge Cases
Encoding mistakes produce invalid or semantically wrong machine code. Operands are masked but not semantically validated. Requires GNU assembler syntax and runtime CPU feature availability.

## Test Signals
Assembly success, disassembly matching intended opcodes, CPU feature gating, and known-answer CRC/checksum tests.
