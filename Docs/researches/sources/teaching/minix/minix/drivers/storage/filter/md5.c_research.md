# File Research: sources/teaching/minix/minix/drivers/storage/filter/md5.c

## Purpose
Provides a public-domain MD5 implementation used by the filter driver for per-sector checksums.

## Key Behavior
- Implements `MD5Init()`, `MD5Update()`, `MD5Final()`, and `MD5Transform()`.
- Uses portable little-endian load/store helpers that do not require an exact 32-bit C integer type.
- Maintains bit counts, buffers partial 64-byte blocks, pads final input, appends length, emits a 16-byte digest, and clears the context.
- Contains the standard four MD5 round functions and `MD5STEP` macro.
- Optional `#ifdef TEST` standalone test program hashes command-line strings.

## Integration Notes
Used by `sum.c` for `ST_MD5`, where the sector number is included in the digest input. Header is `md5.h`.

## Risks
MD5 is used here as an integrity checksum, not for cryptographic security. Any change would break existing checksum layout compatibility.
