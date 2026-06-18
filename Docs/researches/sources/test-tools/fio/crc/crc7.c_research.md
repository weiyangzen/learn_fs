## sources/test-tools/fio/crc/crc7.c

Purpose: implements CRC-7 using polynomial `x^7 + x^3 + 1`.

Important API and flow: defines `crc7_syndrome_table[256]` and `fio_crc7(const unsigned char *buffer, unsigned int len)`, which iterates bytes through the inline `crc7_byte()` helper.

State and persistence: no mutable state; constant lookup table.

Dependencies and integration: depends on `crc7.h`; used by CRC selection/tests and any protocol needing CRC-7.

Risks and test signals: CRC-7 variants differ in final bit placement and seed; callers must match fio's helper convention. CRC test vectors are the signal.
