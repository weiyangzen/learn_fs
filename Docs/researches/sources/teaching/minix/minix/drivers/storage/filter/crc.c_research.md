# File Research: sources/teaching/minix/minix/drivers/storage/filter/crc.c

## Purpose
Provides a CRC32-like checksum helper for the filter driver.

## Key Behavior
- Contains a static CRC table derived from `cksum.c`.
- `compute_crc()` iterates bytes, indexes the table from the high byte of the running checksum XOR input byte, and updates `s = (s << 8) ^ crctab[i]`.
- Special-cases intermediate zero table indexes by substituting values from a rotating auxiliary sequence.

## Integration Notes
Used by `sum.c` when checksum type is `ST_CRC`. The result is later XORed with the logical sector number before storage.

## Risks
This is not a generic library API; it is a specific checksum routine chosen for the filter layout. The zero-index substitution is unusual and must remain consistent with existing on-disk checksums.
