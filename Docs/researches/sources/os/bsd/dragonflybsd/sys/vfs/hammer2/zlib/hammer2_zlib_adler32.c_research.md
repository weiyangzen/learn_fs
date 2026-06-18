# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_adler32.c

Vendored zlib Adler-32 checksum implementation used by HAMMER2’s zlib compressor/decompressor.

Key responsibilities:
- Implements `adler32()` for running Adler-32 checksum updates over byte buffers.
- Implements `adler32_combine()` and `adler32_combine64()` via shared `adler32_combine_()` for combining checksums of concatenated streams.
- Provides optimized short-length and block-processing paths.

Important implementation details:
- Uses `BASE = 65521` and `NMAX = 5552` to bound modulo operations within 32-bit arithmetic.
- Special-cases one-byte updates and null-buffer initialization.
- Processes large inputs in `NMAX` chunks with unrolled `DO16` byte accumulation.
- Supports a `NO_DIVIDE` path using reduction macros instead of `% BASE`.
- Negative combine lengths return `0xffffffffUL` as an invalid checksum clue.

Dependencies:
- Includes `hammer2_zlib_zutil.h` for zlib typedefs, `Z_NULL`, and utility definitions.

Notable risks:
- The one-byte fast path reads `buf[0]` before the later null-buffer check; callers must only pass `buf == Z_NULL` with `len == 0`.
- Combine correctness depends on signedness and width of `z_off_t`/`z_off64_t`.
- This is checksum/integrity support, not cryptographic protection.
