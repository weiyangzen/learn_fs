# sources/sync-backup/rsync/zlib/adler32.c

Purpose: bundled zlib Adler-32 checksum implementation and checksum-combine helpers.

Important APIs/functions: exports `adler32()`, `adler32_combine()`, and `adler32_combine64()`. Internal `adler32_combine_()` implements concatenation math for two Adler checksums and a second stream length. Macros `DO1` through `DO16` unroll byte accumulation; `MOD`, `MOD28`, and `MOD63` perform modulo reduction with optional no-division arithmetic.

Control flow and state: `adler32()` handles `buf == Z_NULL` by returning the initial checksum, has a fast single-byte path, a short-buffer path, and a block loop over `NMAX` chunks to avoid 32-bit overflow before modulo. No persistent state is used.

Dependencies and integration: included by bundled zlib and used where rsync links that zlib for compression/checksum support. Risks are mostly upstream zlib portability concerns: integer width assumptions, negative combine lengths returning `0xffffffffUL`, and performance tuning. Test signals are compression/decompression integrity tests and any zlib self-tests/build checks; no dedicated subset test targets Adler directly.
