# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsfu.c

This file provides shared PostScript/PDF font-writing utilities, mostly for glyph enumeration, glyph subset normalization, and outline-font validation.

Enumeration paths:
- `psf_enumerate_list_begin` enumerates an explicit glyph list, a CID range, or all font glyphs.
- `psf_enumerate_bits_begin` enumerates selected CIDs/TrueType glyph indices from a bit vector, a range, or all font glyphs.
- `psf_enumerate_glyphs_reset` and `psf_enumerate_glyphs_next` expose a common iterator API used by the CFF and TrueType writers.

Subset utilities:
- `psf_add_subset_pieces` appends composite glyph components, supporting Type 1 `seac` pieces and TrueType composite pieces.
- `psf_sort_glyphs` sorts glyph IDs and removes duplicates.
- `psf_sorted_glyphs_index_of` and `psf_sorted_glyphs_include` provide binary-search membership checks.

Outline validation and collection:
- `psf_check_outline_glyphs` verifies selected glyphs are writable as outline charstrings. It rejects procedure-backed CharStrings, unsupported nonstandard OtherSubrs, and CDevProc-dependent glyphs through the font's `glyph_data` and `glyph_info` callbacks.
- `psf_get_outline_glyphs` copies subset lists into owned storage when needed, validates writability, detects `.notdef`, adds subset component pieces, removes undefined glyphs, sorts the result, and guarantees `.notdef` for subsets.

This file is pure support code for font embedding. It does no direct output-format work beyond preparing the glyph order and metadata that the sibling writers serialize.
