## sources/test-tools/fio/crc/crc16.h

Purpose: header for fio's CRC-16 routine and byte-step helper.

Important API: declares `crc16_table`, `fio_crc16()`, and inline `crc16_byte(crc, data)` which indexes `(crc ^ data) & 0xff` and shifts the running CRC.

State and persistence: no state beyond the external constant table.

Dependencies and integration: included by `crc16.c` and any code needing byte-at-a-time CRC-16 updates.

Risks and test signals: exposing the table and byte helper makes variant coupling visible to callers. Compile coverage plus known-answer vectors validate it.
