# File Research: sources/os/linux/linux-stable/fs/hfsplus/tables.c

## Role

Static Unicode lookup data used by HFS+ filename comparison, case folding, decomposition, and composition. The tables are consumed by `unicode.c`.

## Exported Tables

- `u16 hfsplus_case_fold_table[]`
  - Starts at line 15.
  - Comment says the Unicode case folding table is taken from Apple Technote #1150.
  - Layout:
    - 256-entry high-byte table.
    - Followed by 256-entry subtables for high-byte ranges that have case mappings or ignorable characters.
    - High-byte table value `0` means no mapping/ignorable entries for that high byte.
    - Ignorable characters map to zero.
  - Used by `case_fold()` in `unicode.c`.
- `u16 hfsplus_decompose_table[]`
  - Starts at line 411.
  - Multi-level nibble-indexed decomposition lookup table.
  - Contains base table, per-range pointer tables, and packed decomposition entries.
  - Encodes decomposition lengths in low bits of offsets and points into the trailing decomposed-character data.
  - Used by `hfsplus_decompose_nonhangul()` in `unicode.c`.
- `u16 hfsplus_compose_table[]`
  - Starts at line 1072 and runs to EOF.
  - Trie-like composition table used to convert decomposed sequences back to precomposed Unicode where HFS+ display/export behavior wants composition.
  - Begins with a base table keyed by combining marks and includes a Hangul marker entry.
  - Contains many nested continuation tables for multi-codepoint compositions.
  - Ends with explicit composed results for longer Greek and other multi-mark sequences.
  - Used by `hfsplus_compose_lookup()` and `hfsplus_uni2asc()`.

## Data Coverage

The tables cover:

- ASCII and Latin case mappings.
- Greek, Cyrillic, Armenian, Georgian, fullwidth forms, and other case-folding blocks.
- Canonical decompositions for Latin accented forms, Greek polytonic forms, Indic scripts, Hebrew presentation forms, Japanese voiced/semi-voiced kana, Tibetan combinations, and many multi-mark Latin/Greek sequences.
- Composition support for single and chained combining marks, including Hangul composition marker support handled algorithmically in `unicode.c`.

## Dependencies

Includes only `hfsplus_fs.h`, which declares the external arrays for other HFS+ files.

## Research Notes

This file is generated/static data rather than executable logic. Correctness depends on the lookup formats matching the algorithms in `unicode.c`:

- `case_fold(c)` indexes high byte then low byte.
- `hfsplus_decompose_nonhangul()` walks four 4-bit levels and interprets packed offset/length values.
- `hfsplus_compose_lookup()` binary-searches child tables containing `(codepoint, offset)` pairs.

Any modification to table layout requires coordinated changes in `unicode.c`.
