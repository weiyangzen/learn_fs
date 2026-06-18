# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bitops.c

Implements portable byte-addressed bitmap primitives used by libext2fs. The public functions set, clear, and test single bits for both 32-bit offsets (`ext2fs_set_bit`, `ext2fs_clear_bit`, `ext2fs_test_bit`) and 64-bit offsets (`ext2fs_set_bit64`, `ext2fs_clear_bit64`, `ext2fs_test_bit64`).

The functions operate little-bit-first within each byte and return the previous bit value for set/clear/test style callers. `ext2fs_warn_bitmap` conditionally reports bitmap misuse through `com_err` unless `OMIT_COM_ERR` is defined.

The file also provides `ext2fs_bitcount`, which counts set bits in a byte range using local `popcount8` and `popcount32` helpers. It aligns to a 32-bit boundary, processes 32-bit words, then handles trailing bytes.

Dependencies: `config.h`, `ext2_fs.h`, `ext2fs.h`; uses `uintptr_t`, `__u32`, and `__u64`.

Implementation notes:
- No bounds checking is performed here; callers must ensure the bit offset is inside the backing allocation.
- The bit ordering is intentionally portable across endian variants because it manipulates bytes directly.
- The `while (nbytes > 4)` loop processes only when more than four bytes remain, leaving exactly four bytes to the byte tail path.
