# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_sequences.h

## Role

Private header declaring sequence compression helpers for FSE table selection, table construction, cost estimation, and sequence bitstream encoding.

## Exposed Types

- `ZSTD_defaultPolicy_e`
  - `ZSTD_defaultDisallowed`
  - `ZSTD_defaultAllowed`

This controls whether default zstd FSE tables may be selected for a given symbol stream.

## Exposed Functions

- `ZSTD_selectEncodingType()`
  - Chooses basic, RLE, repeated, or compressed FSE representation.
- `ZSTD_buildCTable()`
  - Builds/copies the selected FSE compression table and writes table metadata when needed.
- `ZSTD_encodeSequences()`
  - Encodes sequence symbols and extra bits into the final bitstream.
- `ZSTD_fseBitCost()`
  - Estimates repeat-table encoding cost.
- `ZSTD_crossEntropyCost()`
  - Estimates default-table encoding cost.

## Dependencies

- Includes `fse.h` for FSE table and repeat-mode types.
- Includes `zstd_internal.h` for symbol encoding types, strategy enums, sequence definitions, and shared constants.

## ReactOS/Btrfs Relevance

This header is used by `zstd_compress.c` to compress the sequence portion of each zstd block produced for Btrfs zstd compression.

## Risks and Notes

- Internal-only API; callers must pass symbol counts, max values, code tables, and entropy workspace consistent with the current block.
- The functions declared here are tightly coupled to zstd block format constants and FSE table layouts.
