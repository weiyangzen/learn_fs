# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sctp_crc32.c

## Purpose

Provides SCTP CRC32c-style checksum support using the reflected polynomial required by RFC 3309 and a four-table word-at-a-time algorithm.

## Key Interfaces

- `sctp_crc32_init()` builds four 256-entry CRC tables from `SCTP_POLY`.
- `sctp_crc32()` updates a supplied CRC over a byte buffer, handling unaligned leading/trailing bytes and aligned word chunks.
- Internal helpers `reflect_32()`, `sctp_crc_byte()`, and `sctp_crc_word()` perform bit reflection and byte/word updates.
- `flip32()` is compiled only for big-endian systems.

## Dependencies

Only depends on fixed-width kernel integer types and endian compile-time selection.

## Notes for Future Work

- `sctp_crc32()` aligns by processing leading bytes before casting to `uint32_t *`.
- Big-endian and little-endian table layout differs, so checksum changes should be verified on both endian modes.
