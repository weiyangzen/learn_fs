# File Research: sources/os/linux/linux/fs/hfsplus/tables.c

## Role

Provides static Unicode lookup tables used by `unicode.c` for HFS+ name comparison, case folding, decomposition, and composition.

## Exported Data

- `u16 hfsplus_case_fold_table[]` (starts at line 15)
  - Case folding table from Apple Technote #1150.
  - Layout is a 256-entry high-byte table followed by 256-entry subtables.
  - A high-byte entry of zero means no case mapping or ignorable characters for that block.
  - Ignorable characters map to zero.
  - Used by `case_fold()` in `unicode.c`, then by case-insensitive catalog comparison, dentry hashing, and dentry comparison.
- `u16 hfsplus_decompose_table[]` (starts at line 411)
  - Multi-level decomposition lookup table for non-Hangul Unicode characters.
  - Encodes top-level and nested table offsets followed by decomposition sequences.
  - Used by `hfsplus_decompose_nonhangul()` in `unicode.c`.
- `u16 hfsplus_compose_table[]` (starts at line 1072)
  - Composition lookup table for recomposing decomposed HFS+ Unicode sequences when presenting names through Linux.
  - Includes a base table of combining marks, nested lookup records, a Hangul marker (`0xffff`), and many direct composed-codepoint leaves.
  - Used by `hfsplus_compose_lookup()` and `hfsplus_uni2asc()`.

## Integration

The file includes only `hfsplus_fs.h`, which declares the arrays as externs for other HFS+ files. There is no executable code in this file; all behavior is in `unicode.c`.

## Research Notes

These tables are part of HFS+ on-disk compatibility rather than generic modern Unicode normalization. Changes here would affect catalog ordering, case-insensitive lookup behavior, dentry hash stability, and Linux-visible filename conversion. Because HFS+ normalization historically follows Apple’s fixed Unicode behavior, these tables should be treated as format data, not tunable locale policy.
