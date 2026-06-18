# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsfu.c

This file provides shared PostScript/PDF font-writing utilities, mostly around glyph enumeration and subset normalization.

Key enumeration paths:
- `psf_enumerate_list_begin` starts enumeration over an explicit glyph list, a CID range, or the full font.
- `psf_enumerate_bits_begin` starts enumeration over a bit vector of selected CIDs/TT glyphs, a CID range, or the full font.
- `psf_enumerate_glyphs_reset` and `psf_enumerate_glyphs_next` provide the common iteration API.

Subset utilities:
- `psf_add_subset_pieces` appends component glyphs for composite glyphs, ensuring pieces needed by `seac` or composite TrueType glyphs are present.
- `psf_sort_glyphs` sorts glyph IDs and removes duplicates.
- `psf_sorted_glyphs_index_of` and `psf_sorted_glyphs_include` provide binary-search lookup.

Outline validation:
- `psf_check_outline_glyphs` verifies selected glyphs can be represented as outline charstrings and do not depend on unsupported behavior such as PostScript-procedure CharStrings, non-standard OtherSubrs, or CDevProc.
- `psf_get_outline_glyphs` gathers Type 1/Type 2 outline glyph metadata, detects `.notdef`, copies subset lists into owned storage, adds subset pieces, removes undefined glyphs, sorts, and guarantees `.notdef` for subsets.

This file is pure support code for font embedding. It does no direct device or filesystem work beyond participating in serialized output managed elsewhere.
