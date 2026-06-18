# sources/storage-engines/rocksdb/util/ppc-opcode.h

## Purpose
Defines PowerPC/VSX instruction encoding macros for assemblers that need explicit `.long` encodings of particular PPC vector instructions.

## Important APIs, Types, And Functions
Register-field macros `__PPC_RA`, `__PPC_RB`, `__PPC_XA`, `__PPC_XB`, `__PPC_XS`, and `__PPC_XT` assemble register indices into instruction bit fields. `VSX_XX3` and `VSX_XX1` combine VSX register fields. Opcode constants cover `VPMSUMW`, `VPMSUMD`, `MFVSRD`, and `MTVSRD`. Public instruction macros emit `.long PPC_INST_* | encoded_operands`.

## Control Flow
There is no C++ control flow. These are preprocessor macros consumed inside assembly contexts.

## State And Persistence
No state is stored. The macros affect emitted machine code at compile/assembly time.

## Dependencies And Integration Points
No includes beyond the license guard. This header is intended for PPC-specific optimized code paths, likely hashing/checksum routines that need vector polynomial multiply and VSX register transfer opcodes.

## Risks
Macros are untyped and can be misused with out-of-range register numbers; masking truncates values to field widths. The `.long` expansion is assembler-specific and only valid in the right architecture and inline-assembly context. Incorrect encodings produce illegal instructions or silent data corruption in low-level optimized paths.

## Test Signals
No direct test in this subset. Coverage is expected through PPC builds and tests of optimized checksum/hash code paths that include this header.
