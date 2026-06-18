# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_unicode.c

## Summary
Provides a static Unicode 5.0 simple/common case-folding table for msdosfs filename handling. The file is data-oriented: it defines source-to-folded 16-bit Unicode codepoint pairs for codepoints in the BMP and exports the number of table entries.

## Main Responsibilities
- Embed Unicode case folding data derived from Unicode 5.0 `CaseFolding.txt`.
- Cover simple/common folding mappings for Latin, Greek, Cyrillic, Armenian, Georgian, Coptic, fullwidth Latin, Roman numerals, and related BMP characters present in the table.
- Expose the table as `msdosfs_unicode_foldmap[]`.
- Expose `msdosfs_unicode_foldmap_entries` as the array element count.

## Key Interfaces
- `const u_int16_t msdosfs_unicode_foldmap[]`.
- `size_t msdosfs_unicode_foldmap_entries`.

## Risks
The table is frozen to Unicode 5.0-era data and only represents simple/common folding, not full case folding expansions. Consumers must interpret the flat array as key/value pairs; the exported entry count is the raw element count, not a count of mapping pairs unless callers divide by two. The table only covers 16-bit codepoints, so supplementary-plane Unicode folding is outside this file's scope.
