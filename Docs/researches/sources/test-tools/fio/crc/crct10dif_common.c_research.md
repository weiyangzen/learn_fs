## sources/test-tools/fio/crc/crct10dif_common.c

Purpose: implements T10 DIF CRC16, optionally delegating to ISA-L.

Important API and flow: when `CONFIG_LIBISAL` is configured, `fio_crc_t10dif()` calls `crc16_t10dif()`. Otherwise it defines a 256-entry table for generator polynomial `0x8bb7` and iterates bytes as `(crc << 8) ^ table[((crc >> 8) ^ byte) & 0xff]`.

State and persistence: no mutable state; table is file-local constant data.

Dependencies and integration: includes ISA-L `<isa-l/crc.h>` or local `crc-t10dif.h`. Used by fio verify/checksum code and CRC tests.

Risks and test signals: ISA-L and table paths must produce identical values for seeded/incremental calls. Known T10 DIF vectors and ISA-L parity tests validate this file.
