## sources/test-tools/fio/crc/crc7.h

Purpose: header for CRC-7 table, byte-step helper, and whole-buffer function.

Important APIs: declares `crc7_syndrome_table`, inline `crc7_byte(crc, data)` using `crc7_syndrome_table[(crc << 1) ^ data]`, and `fio_crc7()`.

State and persistence: no state beyond external constant table.

Dependencies and integration: included by `crc7.c` and callers needing incremental byte updates.

Risks and test signals: inline helper exposes the exact shift/index convention. Known-answer tests should include incremental and whole-buffer use.
