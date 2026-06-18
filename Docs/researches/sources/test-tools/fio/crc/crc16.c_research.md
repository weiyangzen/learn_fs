## sources/test-tools/fio/crc/crc16.c

Purpose: table-driven standard CRC-16 implementation with polynomial `0x8005` and initial CRC zero.

Important API and flow: exports the 256-entry `crc16_table` and `fio_crc16(const void *buffer, unsigned int len)`. The function walks bytes and applies the inline `crc16_byte()` helper from the header.

State and persistence: no mutable state; the table is constant global data.

Dependencies and integration: depends on `crc16.h`. Used by fio's verification/hash selection and the CRC benchmark/test harness.

Risks and test signals: this computes a specific reflected table variant, so callers must not assume another CRC-16 flavor. Known-answer CRC tests in `crc/test.c` are the key signal.
