# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crc32.h

## Role

Defines CRC32 theory notes, table-generation/computation macros, the standard Solaris CRC32 polynomial, and the kernel precomputed table declaration.

## Main Macros

- `CRC32_INIT(table, poly)`: fills a 256-entry `uint32_t` lookup table for a polynomial.
- `CRC32(crc, buf, size, start, table)`: computes CRC over a byte buffer.
- `CRC32_STRING(crc, len, str, start, table)`: computes CRC over a NUL-terminated string and records length.
- `CRC32_POLY`: `0xEDB88320U`.
- `CRC32_TABLE`: full precomputed 256-entry table for `CRC32_POLY`.

## Kernel Interface

- `extern const uint32_t crc32_table[256];`

## Behavior Notes

- Documentation explains initial value choice, polynomial constraints, bitwise algorithm, bytewise algorithm, and lookup-table optimization.
- Macros use local variable names prefixed with `X` to reduce caller collision risk, but they are still statement-like macro blocks.

## Research Relevance

CRC32 is common in storage, networking, and metadata checks. This header supplies illumos’s common table/macro implementation.
