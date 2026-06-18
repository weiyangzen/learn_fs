# File Research: sources/virtualization/spdk/lib/util/crc32c.c

This file implements CRC32C update helpers with ISA-L, x86 SSE4.2, ARM CRC, or table fallback dispatch selected at compile time.

With ISA-L, `spdk_crc32c_update()` calls `crc32_iscsi()`. With SSE4.2, it processes unaligned head bytes using `_mm_crc32_u8`, aligned 64-bit words using `_mm_crc32_u64`, and tail bytes using `_mm_crc32_u8`. With ARM CRC instructions, it uses `__crc32cb` for bytes and `__crc32cd` for aligned 64-bit words. Without hardware support, a constructor initializes a reflected Castagnoli table and update delegates to `crc32_update()`.

`spdk_crc32c_iov_update()` folds CRC32C across an iovec array, returning the input CRC unchanged for a null iovec and asserting non-null/nonzero entries otherwise. `spdk_crc32c_nvme()` applies the NVMe-style complement convention: it updates with `~crc` and returns the complement of the result.

Important invariants are caller-provided initial CRC semantics, alignment-aware hardware loops, and compile-time feature selection from `crc_internal.h`.
