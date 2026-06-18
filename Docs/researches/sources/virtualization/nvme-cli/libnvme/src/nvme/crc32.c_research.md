# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/crc32.c

CRC-32 implementation derived from Gary S. Brown’s public-domain style code and FreeBSD libkern lineage.

Contents:
- `crc32_tab[]`: 256-entry lookup table for polynomial `0xedb88320`.
- `crc32(crc, buf, size)`: inverts the starting CRC, updates over bytes with the table, and returns inverted result.

Integration:
- Used by `crypto.c` to append and verify CRC values in NVMe TLS key interchange strings.

Behavior:
- Supports incremental CRC by accepting an initial CRC.
- `crc32(0, NULL, 0)` is safe because the loop does not dereference the buffer for zero size.
- The function treats input as raw bytes.

Risks and tests:
- Correctness should be verified against standard CRC-32 vectors and the TLS key import/export round trip.
- The global table is not declared `static`, so it is externally visible unless hidden by build visibility settings.
