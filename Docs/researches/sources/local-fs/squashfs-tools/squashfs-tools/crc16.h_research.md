# File Research: sources/local-fs/squashfs-tools/squashfs-tools/crc16.h

Header for the CRC16 helper.

Exports:
- `get_checksum(char *buff, int bytes, unsigned short chksum)`

Notable quirk:
- Include guard is named `HASH_H`, not `CRC16_H`, which is harmless only if no unrelated header uses the same guard name.
