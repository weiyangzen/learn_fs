# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast_checksum.c

`hast_checksum.c` implements optional data checksumming for HAST protocol payloads.

Key behavior:
- Supports checksum names `none`, `crc32`, and `sha256`.
- CRC32 uses zlib `crc32()`.
- SHA256 uses FreeBSD SHA256 routines.
- `checksum_send()` computes the selected hash for outgoing data, adds `checksum` and `hash` nv fields, and leaves payload data unchanged.
- `checksum_recv()` verifies incoming payload data against `checksum` and `hash` nv fields.
- Missing checksum field means no checksum was used.
- Unknown algorithms, missing hash, invalid hash size, or mismatch fail receive validation.

Important details:
- CRC32 stores the native `uint32_t` bytes with a comment questioning endian conversion.
- Max hash stack buffer size is SHA256 digest length.
