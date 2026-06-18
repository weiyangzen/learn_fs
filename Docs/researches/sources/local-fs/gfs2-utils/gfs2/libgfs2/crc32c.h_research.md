# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/crc32c.h

Small public header for CRC-32C support.

Exports:
- `uint32_t crc32c(uint32_t seed, unsigned char const *data, size_t length);`
- `void crc32c_optimization_init(void);`

Integration role:
- Included by `structures.c` for GFS2 journal log-header CRC generation.
- Pulls in `stdlib.h` and `inttypes.h`.

Risk notes:
- Signature changes affect journal checksum generation.
- Header does not document seed/finalization expectations; callers must follow existing CRC-32C usage.
