# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcopy.c

Implements Ghostscript font copying/subsetting for high-level output devices.

Key behavior:
- Defines copied-font private data for glyph byte strings, glyph names, extra glyph aliases, copied font metadata, Type 1/CFF subrs, TrueType/CID backing data, encodings, and CID maps.
- Provides GC descriptors for copied glyph arrays, name arrays, extra-name lists, and copied-font data.
- `gs_copy_font` creates a copied font shell for Type 1/2, Type 42 TrueType, CIDFontType 0, and CIDFontType 2 fonts without copying all glyphs up front.
- `gs_copy_glyph_options` copies one glyph and recursively copies component glyphs discovered through `psf_add_subset_pieces`.
- Type 1/2 path copies local/global subrs, charstrings, glyph names, `.notdef`, and provides glyph-data/subr/seac accessors for the copied font.
- Type 42 path writes stripped TrueType/CID2 font data to memory, stores glyph outlines separately, fakes hmtx/vmtx metrics space, and maps names to GIDs.
- CIDFontType 0 path copies FDArray subfonts and shares parent glyph/subr storage with copied subfonts.
- CIDFontType 2 path maintains an expandable `CIDMap` from copied CIDs to TrueType GIDs.
- `gs_copy_font_complete` enumerates all glyphs and copies Encoding entries where relevant.
- `gs_copied_can_copy_glyphs` checks whether glyph subsets can be merged by comparing font type/name/WMode, optional hinting data, and glyph outlines/metrics.
- `copied_drop_extension_glyphs` removes synthetic extension glyphs used to resolve PDF Widths-to-Metrics name conflicts before embedding.

Dependencies:
- Uses core font structures from `gxfont.h`, `gxfont1.h`, `gxfont42.h`, and CID support from `gxfcid.h`.
- Uses glyph cache marking through `gs_font_dir`.
- Uses Type 1 interpreter support for outlining copied Type 1 glyphs.
- Uses `gdevpsf.h` subset/piece discovery and stripped TrueType/CID writing helpers.
- Uses Ghostscript memory, GC, string, matrix, path, and graphics-state APIs.

Research notes:
- Copied fonts deliberately do not support `make_font`; they support querying, glyph outlining, and BuildChar-style rendering for already copied glyphs.
- Type 1 glyph-name lookup uses hashed storage sized to prime values to guarantee reprobe termination.
- TrueType copied glyph storage is indexed by GID; CIDFontType 2 adds a CID-to-GID layer.
- The compatibility check is important for high-level output font merging and prevents mixing same-named but structurally different fonts.
- Potential risk: `compare_glyphs` contains a suspicious `memcmp(gdata0.bits.data, gdata0.bits.data, ...)`, which compares a buffer with itself rather than with `gdata1`.
- Potential risk: `copied_drop_extension_glyphs` has fragile pointer/string arithmetic in the extension-name separator checks.
