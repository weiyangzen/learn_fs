# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/crc32.h

Internal declaration header for CRC-32.

Exports:
- `uint32_t crc32(uint32_t crc, const void *buf, size_t len);`

Dependencies:
- Includes `<stddef.h>` and `<stdint.h>`.

Integration:
- Included by `crypto.c` for TLS PSK interchange format integrity checks.
- Not marked as a public libnvme API symbol.
