# File Research: sources/local-fs/apfs-fuse/ApfsLib/UnicodeTables_v10.h

This header is generated/static Unicode normalization and case-folding data for `Unicode.cpp`. It contains no functions, only `static const` lookup arrays.

The file begins with `#include <cstdint>` and defines ten arrays:
`nf_trie_hi[0x300]`, `nf_trie_mid[0x7F0]`, `nf_basic_cf[0x500]`, `nf_u16_inv_masks[0x80]`, `nf_trie_lo[0x1910]`, `nf_u16_seq_2[0x610]`, `nf_u16_seq_3[0x2A0]`, `nf_u16_seq_misc[0xC8]`, `nf_u32_char[0x320]`, and `nf_u32_seq_misc[0x54]`.

The trie arrays encode compact lookup states for Unicode code point normalization. Sentinel values such as `0xFFFF`, `0xAC00`, `0xADxx`, `0xAExx`, and high-nibble classes `0xB` through `0xF` are interpreted by `normalizeOptFoldU32Char()` as invalid entries, Hangul decomposition, combining-class entries, invalid-mask entries, direct mappings, or sequence-table references.

`nf_basic_cf` provides simple case-fold mappings for code points below `0x500`, covering ASCII, Latin, Greek, Cyrillic, and adjacent basic ranges used by the normalization code’s fast case-fold path. Higher code point mappings are represented through the trie and UTF-32 mapping arrays.

`nf_u16_seq_2`, `nf_u16_seq_3`, and `nf_u16_seq_misc` store canonical decomposition sequences made of 16-bit code units, including Latin accent decompositions, Greek decompositions, Hebrew marks, Japanese voiced/semi-voiced kana decompositions, ligatures, and other compatibility/canonical sequences. The miscellaneous table stores length metadata in-band.

`nf_u32_char` and `nf_u32_seq_misc` store mappings requiring 32-bit code points, including supplementary-plane case folds and decompositions. `Unicode.cpp` selects these for table entries whose class requires UTF-32 output.

Because this header is static table data, its correctness is tightly coupled to the decoder logic in `Unicode.cpp`. Manual edits are high risk unless regenerated from the same Unicode/APFS normalization source assumptions.
