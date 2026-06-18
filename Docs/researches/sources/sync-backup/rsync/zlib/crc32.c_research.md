# sources/sync-backup/rsync/zlib/crc32.c

Purpose: bundled zlib CRC-32 implementation, including optional dynamic table generation, endian-optimized word-at-a-time paths, and CRC combination.

Important APIs/functions: exports `get_crc_table()`, `crc32()`, `crc32_combine()`, and `crc32_combine64()`. With `DYNAMIC_CRC_TABLE`, `make_crc_table()` computes the polynomial tables and can emit `crc32.h` under `MAKECRCH`; otherwise it includes the static table header. `crc32_little()` and `crc32_big()` handle BYFOUR optimized processing. `gf2_matrix_times()`, `gf2_matrix_square()`, and `crc32_combine_()` combine CRCs for concatenated streams.

Control flow and state: static CRC tables are either compiled in or lazily generated. The dynamic-generation path uses volatile flags but is explicitly not fully thread-safe unless initialized before concurrent use. `crc32()` returns zero for `Z_NULL`, xor-initializes/finalizes the CRC, selects endian path when safe, and falls back to byte/DO8 loops.

Dependencies and integration: used by bundled zlib inflate/deflate/gzip-adjacent code and possibly checksum utilities. Risks include dynamic-table concurrency, pointer alignment/endian assumptions in BYFOUR, and length semantics for combine (`len2 <= 0` returns `crc1`). Test signals are zlib compatibility, decompression integrity, and any CRC table generation checks; rsync compressed-transfer tests indirectly exercise it.
