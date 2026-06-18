# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_sequences.c

## Role

Implements sequence entropy-table selection, FSE table construction, and final bitstream encoding for zstd match sequences. It is the sequence-side counterpart to literal compression.

## Main Components

- `kInverseProbabilityLog256`
  - Lookup table used for approximate entropy cost calculations.
- `ZSTD_fseBitCost()`
  - Estimates the cost of encoding symbols using an existing FSE table.
  - Rejects repeat tables that cannot represent required symbols.
- `ZSTD_crossEntropyCost()`
  - Estimates cost of encoding a distribution with default normalized counts.
- `ZSTD_selectEncodingType()`
  - Chooses among:
    - `set_basic`
    - `set_rle`
    - `set_repeat`
    - `set_compressed`
  - Uses fast heuristics for lower strategies and cost comparison for lazy/optimal strategies.
- `ZSTD_buildCTable()`
  - Builds or copies the FSE compression table according to selected encoding type.
  - Writes normalized count headers for compressed tables.
- `ZSTD_encodeSequences()`
  - Encodes literal length, match length, and offset code streams into a zstd bitstream.
  - Dispatches to a BMI2-specialized implementation when dynamic BMI2 support is enabled.

## Encoding Flow

1. The caller provides symbol code tables for literal lengths, match lengths, and offsets.
2. `ZSTD_selectEncodingType()` decides how each symbol stream should be represented.
3. `ZSTD_buildCTable()` prepares the FSE table and writes any required table description.
4. `ZSTD_encodeSequences_body()` initializes FSE states from the last sequence.
5. Sequences are encoded in reverse order.
6. Extra bits for literal length, match length, and offset are interleaved with FSE state transitions.
7. FSE states are flushed and the bitstream is closed.

## Long Offset Handling

When `longOffsets` is true, offset extra bits may exceed the safe stream accumulator budget. The encoder splits offset bits into an early flushed portion and a later portion to avoid accumulator overflow, especially on 32-bit builds.

## Dependencies

- Includes `zstd_compress_sequences.h`.
- Uses FSE APIs, BIT stream APIs, entropy constants, and zstd sequence definitions from internal zstd headers.

## ReactOS/Btrfs Relevance

This file emits the compressed sequence section for each zstd block. For Btrfs compressed extents, it is part of the path that converts LZ-style matches into format-compliant zstd block payloads.

## Risks and Notes

- Bitstream ordering is intentionally reverse-sequence order; changing this would break decoding.
- Cost estimation affects compression ratio and speed but must still preserve valid fallback behavior.
- Repeat-table validation is necessary because reused FSE tables may lack symbols required by the current block.
- 32-bit and long-offset flush decisions are format and portability sensitive.
