# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_utfconvdata.h

## Purpose

`vfs_utfconvdata.h` is a generated/static Unicode data header used by XNU VFS UTF conversion code. It contains no executable logic; it supplies compact lookup tables derived from Core Foundation Unicode decomposition, precomposition, and non-base/combining-character data.

The file exists so kernel filename conversion/normalization code can perform Unicode canonical decomposition, canonical composition, and combining-character classification without depending on Core Foundation at runtime.

## Data Provided

- `__CFUniCharDecompositionTable[]`: `u_int16_t` pairs mapping precomposed BMP code points to packed decomposition-table positions or flags.
- `__UniCharDecompositionTableLength`: computed element-pair count for the decomposition table.
- `__CFUniCharMultipleDecompositionTable[]`: ordered `u_int16_t` sequences used for decompositions that expand into multiple code units, including Latin diacritics, Greek, Cyrillic, Arabic, Indic scripts, Tibetan, Kana voiced/semi-voiced forms, Hebrew presentation forms, and others.
- `__CFUniCharDecomposableBitmap[]`: bitmap/index data for fast checks that a code point is decomposable before doing table lookup.
- `__CFUniCharPrecompSourceTable[]`: `u_int32_t` records keyed by combining marks, carrying packed offsets/counts into destination precomposition tables.
- `__CFUniCharPrecompositionTableLength`: computed pair count for precomposition source records.
- `__CFUniCharBMPPrecompDestinationTable[]`: base-code-point plus precomposed-result pairs for BMP canonical composition.
- `__CFUniCharCombiningBitmap[]`: bitmap/index data identifying combining characters/non-base characters.
- `__CFUniCharCombiningPropertyBitmap[]`: compact combining-class/property table used to order or classify non-base marks.

## Control Flow

There is no control flow in this file. Consumers include it and interpret the table formats. The only computations are compile-time `sizeof(...)` length constants.

## State and Invariants

- The table layout is positional and tightly coupled to the UTF conversion implementation that consumes it. Reordering entries or changing element widths changes semantics.
- `u_int16_t` tables assume BMP-oriented code unit representation for these normalization tables; packed values such as high-bit-prefixed entries are meaningful to the consumer.
- Length constants divide by pair widths, so callers likely iterate by logical mapping records, not raw element count.
- The header has no include guard because it is data intended for direct inclusion in one implementation context rather than a public multi-include interface.

## Dependencies

The file depends only on kernel integer typedefs (`u_int8_t`, `u_int16_t`, `u_int32_t`) being available before inclusion. Its comments identify Core Foundation source headers as the data origin: `CFUniCharDecompData.h`, `CFUniCharPrecompData.h`, and `CFUniCharNonBaseData.h`.

## Risks and Edge Cases

- Unicode correctness depends on the consuming code and this generated data staying in sync. Updating one without the other can silently corrupt filename normalization.
- The data appears static and versioned by the source snapshot, not by an explicit Unicode version marker in the file.
- Because it is mostly numeric data, review must focus on table shape, lengths, and generator provenance rather than individual value semantics.
- Any accidental formatter, sort, or line-wrap change that alters values would be hard to catch without normalization regression tests.

## Research Notes

The entire 1,697-line file was read. No per-file output was generated separately in this pass.
