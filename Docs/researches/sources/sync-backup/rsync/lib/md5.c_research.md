# sources/sync-backup/rsync/lib/md5.c

Purpose: RFC 1321-compatible MD5 implementation used by rsync checksums when OpenSSL or another digest path is not used, with optional x86-64 assembly acceleration for full blocks.

Important APIs/types/functions: `md5_begin`, `md5_update`, `md5_result`, static `md5_process`, optional external `md5_process_asm`, static `md5_padding`, and `TEST_MD5` helpers/main.

Control flow: `md5_begin` initializes A/B/C/D and bit counters. `md5_update` updates byte counters, fills a partial 64-byte buffer if present, sends full blocks through assembly or `md5_process`, and stores any remainder. `md5_process` decodes 16 little-endian words and performs all four MD5 rounds using macros. `md5_result` appends padding and the 64-bit bit length, then writes the little-endian digest.

State and persistence behavior: all digest state lives in caller-owned `md_context`. `totalN` and `totalN2` track byte count overflow; `buffer` stores partial chunks. No persistent storage.

Dependencies/integration: includes `rsync.h` for `md_context`, integer helpers, and endian macros. Used from checksum code, and optionally paired with `md5-asm-x86_64.S`.

Risks/test signals: this is not suitable as a security primitive, but rsync uses it for checksums/protocol compatibility. Edge cases include length counter overflow, exact 56/64-byte padding boundaries, partial-buffer handling, assembly/C equivalence, and little-endian encoding macros. The file includes RFC 1321 test vectors under `TEST_MD5`.
