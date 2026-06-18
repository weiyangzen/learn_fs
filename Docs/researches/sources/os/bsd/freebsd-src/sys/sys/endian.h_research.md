# File Research: sources/os/bsd/freebsd-src/sys/sys/endian.h

## Purpose
Exports byte-swap macros and alignment-safe little/big-endian encode/decode helpers for 16-, 32-, and 64-bit integers.

## Main Interfaces
- Typedef guards for `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t`.
- `bswap16`, `bswap32`, `bswap64` mapping to machine helpers.
- Decode helpers: `be16dec`, `be32dec`, `be64dec`, `le16dec`, `le32dec`, `le64dec`.
- Encode helpers: `be16enc`, `be32enc`, `be64enc`, `le16enc`, `le32enc`, `le64enc`.

## Dependencies And Integration
Includes `sys/cdefs.h`, `sys/_types.h`, and `machine/endian.h`. The inline helpers operate byte-by-byte and are safe for unaligned bytestreams, making them useful for filesystem, network, disk-label, and protocol parsing.

## Risk Notes
This header intentionally does not avoid namespace pollution because non-POSIX consumers rely on these macros. Edits must preserve exact byte ordering and avoid introducing alignment assumptions.
