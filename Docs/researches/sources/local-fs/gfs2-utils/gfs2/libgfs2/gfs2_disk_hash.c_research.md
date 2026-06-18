# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/gfs2_disk_hash.c

This file implements GFS2's on-disk directory/hash CRC.

Public API:
- `lgfs2_disk_hash(const char *data, int len)`

Behavior:
- Uses a standard CRC-32 table.
- Starts with `0xffffffff`, updates per byte, then bitwise complements the result.
- Must match kernel `crc32_le(0xFFFFFFFF, data, len) ^ 0xFFFFFFFF`.

Integration role:
- Used for directory entry hashes.
- Used for metadata checks such as resource group CRC and log-header hash.

Risk notes:
- Signed `char` promotion can matter if changed; current implementation uses `(hash ^ *data) & 0xff`.
- Any change breaks directory lookup compatibility and metadata checksum validation.
