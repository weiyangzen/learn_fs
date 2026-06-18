# sources/sync-backup/rsync/simd-checksum-avx2.S

Purpose: Optional AVX2 assembly implementation of rsync's rolling checksum inner loop when `USE_ROLL_ASM` is enabled.

Important APIs, types, and functions: Exports `get_checksum1_avx2_asm` (with leading underscore on Apple). The function receives `buf`, `len`, current index `i`, and pointers to `ps1`/`ps2`, processes 64-byte chunks after a 128-byte threshold check, updates sums, and returns the updated index. `.mul_T2` stores byte weights 64 down to 1.

Control flow: The routine exits immediately when too little data remains. Otherwise it loads constants and the first two cache lines, loops over 64-byte blocks using AVX2 operations (`vpmaddubsw`, `vpaddw`, `vpaddd`, `vpsrldq`, prefetch), accumulates partial s1/s2 values, performs horizontal reductions, writes back `*ps1` and `*ps2`, calls `vzeroupper`, and returns.

State and persistence behavior: Mutates only caller-provided checksum pointers and uses read-only constant data. No global writable state.

Dependencies and integration points: Includes `config.h`, must match `CHAR_OFFSET` in `rsync.h`, requires assembler/CPU support for AVX2 and non-temporal aligned load instructions used here. Integrated with checksum dispatch/build configuration.

Risks and test signals: Risks include ABI/register convention mismatches, CPU feature dispatch errors, checksum divergence from C implementation, unaligned/short-buffer handling, and `CHAR_OFFSET` drift. Tests should compare checksums against the C path across lengths/alignment, run on AVX2 and non-AVX2 hosts, and include sanitizer-style fallback coverage.
