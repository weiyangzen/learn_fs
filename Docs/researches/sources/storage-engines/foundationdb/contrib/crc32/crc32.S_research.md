# sources/storage-engines/foundationdb/contrib/crc32/crc32.S

## Purpose
PowerPC64 vector assembly implementation of CRC computation using POWER8 VPMSUM instructions and Barrett reduction. It is compiled only when `__powerpc64__` is defined.

## Important APIs, Types, And Functions
The exported assembly symbol is `CRC32_FUNCTION_ASM`, defaulting to `__crc32_vpmsum`. ABI signature is `unsigned int __crc32_vpmsum(unsigned int crc, void *p, unsigned long len)`. It includes `crc32_constants.h` or a macro-provided constants header and uses `ppc-asm.h` / `ppc-opcode.h` macros such as `FUNC_START`, `VPMSUMD`, `VPMSUMW`, `MTVRD`, and `MFVRD`.

## Control Flow
The function saves nonvolatile GPR and VMX registers, prepares masks and optional byteswap constants, folds input in 128-byte chunks into eight parallel vector CRC lanes, reduces accumulated 1024-bit state to 64 bits, handles remaining tail chunks, applies Barrett reduction to produce a 32-bit CRC, restores registers, and returns. A short path handles inputs below 256 bytes; a zero-length path returns the original CRC.

## State And Persistence
No persistent state. Runtime state is entirely register and stack scratch state. It reads static constants from the included generated tables.

## Dependencies And Integration
Used by `crc32_wrapper.c` on PowerPC64. Requires assembler support for Power/VMX opcodes and the constants generated for the selected polynomial/reflection mode.

## Risks
Architecture-specific and ABI-sensitive. Correctness depends on 16-byte alignment expectations handled by the C wrapper and on matching `CRC`, `REFLECT`, and endian macros. The file manipulates TOC-relative symbols and register save areas directly, so toolchain differences can break builds. Non-PowerPC builds rely on the top-level guard producing no code.

## Test Signals
Compare against known CRC32C vectors on ppc64 for aligned, unaligned via wrapper, short, long above `MAX_SIZE`, and zero-length buffers. Build with GCC and Clang assemblers in little- and big-endian Power environments if supported.
