## sources/test-tools/fio/crc/crc32c.c

Purpose: portable table-driven CRC32C (Castagnoli) fallback.

Important API and flow: `crc32c_sw(unsigned char const *data, unsigned long length)` starts with `~0`, processes each byte through `crc32c_table[(crc ^ byte) & 0xff] ^ (crc >> 8)`, and returns the running CRC. The table is generated for polynomial `0x1EDC6F41` with reflected input/output.

State and persistence: no mutable state; local constant table only.

Dependencies and integration: included through `crc32c.h`; used directly as fallback and as macro replacement when hardware paths are unavailable.

Risks and test signals: CRC32C variant must match hardware implementations exactly. Known-answer tests and cross-checking ARM/Intel/software paths are the key signals.
