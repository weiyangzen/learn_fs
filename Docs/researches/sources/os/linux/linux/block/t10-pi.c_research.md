# File Research: sources/os/linux/linux/block/t10-pi.c

## Summary
Implements generation, verification, and request remapping of T10/NVMe protection information tuples for block integrity.

## Main Responsibilities
- Computes guard checksums for CRC64, T10 DIF CRC, and IP checksum formats.
- Generates integrity tuples for outgoing bios.
- Verifies integrity tuples for completed bios.
- Handles metadata layouts with `pi_offset`.
- Supports tuple copies across split protection bvecs.
- Remaps reference tags between virtual bio seeds and request physical positions.

## Key APIs
- `bio_integrity_generate()`.
- `bio_integrity_verify()`.
- `blk_integrity_prepare()`.
- `blk_integrity_complete()`.

## Important Behavior
`blk_integrity_iterate()` walks data bvecs by integrity interval, accumulates checksum over each interval, and then reads or writes the corresponding protection tuple. Extended CRC64 tuples use 64-bit guards and 48-bit reference tags; T10/IP tuples use 16-bit guards and 32-bit reference tags.

Verification honors application/reference tag escape values. When `BLK_INTEGRITY_REF_TAG` is enabled, reference tags must match the current seed unless the app tag escapes checking.

Request prepare maps reference tags from bio-virtual seeds to request reference positions; completion maps them back. Already mapped integrity payloads are detected with `BIP_MAPPED_INTEGRITY`.

## State and Lifetime
All iteration state is local in `struct blk_integrity_iter`. Tuple handling uses stack storage when a tuple crosses protection-vector boundaries and maps bvecs locally otherwise.

## Risks
The code is highly offset-sensitive: `pi_offset`, tuple size, metadata size, interval size, and bvec boundaries must agree with queue integrity limits. Incorrect reference-tag remapping can cause false protection failures or missed corruption detection.
