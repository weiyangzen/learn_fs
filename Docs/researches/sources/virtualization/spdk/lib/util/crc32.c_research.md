# File Research: sources/virtualization/spdk/lib/util/crc32.c

This file provides shared CRC32 table initialization and generic update routines used by CRC32 IEEE and CRC32C fallback paths.

`crc32_table_init()` fills a 256-entry reflected-polynomial lookup table by shifting each byte through eight polynomial steps.

`crc32_update()` has two implementations. On ARM with CRC instructions, it processes unaligned head bytes, aligned 64-bit middle words via `__crc32d`, and tail bytes via `__crc32b`; the table parameter is unused on this path. Otherwise, it performs the standard byte-at-a-time reflected table update: `(crc >> 8) ^ table[(crc ^ byte) & 0xff]`.

Important invariants are reflected polynomial tables and caller-controlled CRC seed/finalization. The hardware path tries to avoid unaligned 64-bit loads by splitting head/middle/tail.
