# sources/storage-engines/rocksdb/util/crc32c_ppc_asm.S

Purpose: PowerPC/Power8 vector assembly implementation of bulk CRC-32C using VPMSUM instructions and Barrett reduction.

Important symbol: exports `__crc32_vpmsum(unsigned int crc, void* p, unsigned long len)`, consumed by `crc32c_ppc.c`. Internal labels handle bulk, short, zero-length, cooldown, and final reduction paths.

Control flow: the function saves GPR and VMX registers, prepares masks/constants, incorporates the initial CRC into vector state, and chooses `.Lshort` for inputs below 256 bytes. Large inputs are processed in MAX_SIZE-bounded blocks using eight parallel 16-byte vector lanes, warm-up/main/cool-down scheduling, tail reduction for 0-112 remaining bytes, and final Barrett reduction. Conditional `BYTESWAP_DATA` selects `vperm` byte swapping based on endianness and reflection.

State and persistence: no persistent state; it preserves nonvolatile registers before returning the CRC in `r3`. Correctness is entirely encoded in constant tables and polynomial/reflection macros.

Dependencies and integration: includes platform assembly helpers (`ppc-asm.h`, `ppc-opcode.h`) and includes `crc32c_ppc_constants.h` in assembly mode. It is linked with the C wrapper only for relevant PowerPC builds.

Risks: high platform sensitivity: ABI register preservation, TOC addressing, endian/reflection modes, and assembler macro compatibility are all critical. The code assumes callers provide aligned bulk ranges after C wrapper preprocessing. Debugging failures can be difficult because most logic is in vector assembly.

Test signals: covered only indirectly by CRC vector tests on Power8 hardware/builds.
