# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/crc32.h

## Purpose
Provides generated static lookup tables for fast CRC-32 calculation.

## Key Elements
Defines `crc_table[TBLS][256]` with the base 256-entry CRC table and additional `BYFOUR` tables for word-at-a-time big/little endian CRC paths.

## Behavior/Risks
This is generated data, not handwritten algorithmic code. Correctness depends on consistency with the polynomial/table-generation logic in `crc32.c`. The table is conditionally sized by `TBLS`, so it must be included in the same macro environment expected by `crc32.c`.

## Dependencies
Included only from `crc32.c`, relying on `local`, `FAR`, and `TBLS` being defined before inclusion.
