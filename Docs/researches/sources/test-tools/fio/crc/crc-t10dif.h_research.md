## sources/test-tools/fio/crc/crc-t10dif.h

Purpose: declares the T10 DIF CRC16 function used for data integrity field checks.

Important API: `fio_crc_t10dif(unsigned short crc, const unsigned char *buffer, unsigned int len)` accepts a seed/current CRC and buffer length so callers can compute incrementally.

State and persistence: no state; pure declaration.

Dependencies and integration: implemented by `crct10dif_common.c`, either through ISA-L when configured or the local table implementation. Used by fio verification/checksum paths and CRC tests.

Risks and test signals: callers must use the correct initial seed for their protocol. ABI is intentionally small; compile and CRC vector tests validate the contract.
