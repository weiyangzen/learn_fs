# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype42.c

Implements Ghostscript Type 42/TrueType font support: font-table discovery, glyph lookup, metrics, glyph enumeration, and outline extraction/rendering helpers.

Key behavior:
- `gs_type42_font_init` validates the TrueType version, scans the table directory, records offsets for `cmap`, `glyf`, `head`, `hhea/hmtx`, `vhea/vmtx`, `loca`, and `maxp`, and installs Type 42 font procedure callbacks.
- Builds `len_glyphs` from the `loca` table and includes a slower fallback for fonts with out-of-order `loca` entries.
- Computes a replacement `FontBBox` from the `head` table when the supplied PostScript bounding box looks invalid.
- Provides default glyph-index mapping for CID/GID-like glyphs and default outline access through `loca`/`glyf`.
- Handles segmented `sfnts` glyph access by copying pieces into a contiguous glyph buffer when needed.
- Supports direct TrueType-file outline extraction through a stream-based helper.
- Parses composite glyph components, component transforms, point-matching arguments, and component metrics inheritance.
- Provides glyph-info APIs for widths, vertical vectors, composite pieces, and glyph enumeration.
- Contains legacy simple-glyph outline parsing from flags/coordinate streams, including quadratic-to-cubic conversion, though the fitted outline path delegates to `gx_ttf_outline`.

Dependencies:
- Uses TrueType constants and interpreter support from `gxttf.h`, `gxttfb.h`, `gxfont42.h`, and font-cache helpers from `gxfcache.h`.
- Uses `gsutil.c`'s `get_u32_msb` for big-endian table parsing.
- Uses path and matrix APIs for outline construction and coordinate transforms.

Research notes:
- Name glyph lookup is not implemented in the default glyph-index callback.
- `parse_component` contains an explicit fixed-matrix layout hack for transformed component translations.
- Stream-based outline extraction notes repeated per-glyph reads and suggests caching.
- `gs_type42_glyph_outline` notes that subpixel scale cannot pass through the `font_proc_glyph_outline` interface, so it applies design-grid behavior for current callers.
