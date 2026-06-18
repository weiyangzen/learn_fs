# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsft.c

This file writes embedded TrueType data from Ghostscript Type 42 and CIDFontType 2 fonts. It can output normal TrueType fonts, stripped TrueType fonts, CIDFontType 2 fonts, and stripped CIDFontType 2 fonts.

Core responsibilities:
- Copy existing TrueType tables through `string_proc`.
- Rebuild `glyf` and `loca` tables from selected glyph outlines.
- Synthesize missing `cmap`, `name`, `OS/2`, `hmtx`/`vmtx`, and `post` tables when requested or needed.
- Sort table-directory records and write a complete sfnt header/table directory.
- Support subset glyph closure by adding composite glyph pieces before writing subsets.

Important helper groups:
- Big-endian table writing: `put_ushort`, `put_ulong`, `put_loca`, `put_u16`, `put_u32`.
- Table copying: `write_range` reads segmented font data safely through `pfont->data.string_proc`.
- Generated cmap support: writes Macintosh format 0 or 6 tables plus Windows format 4 table, with optional private-use bias `0xf000`.
- Metrics: `size_mtx` computes compact metrics table size from glyph metrics; `write_mtx` emits h/v metrics.
- Name/OS2/post: `write_name`, `write_OS_2`, `update_OS_2`, `compute_post`, and `write_post`.

Main implementation is `psf_write_truetype_data`. It:
1. Reads and filters the existing table directory.
2. Extracts `head`, `maxp`, existing table presence, and original table offsets.
3. Enumerates glyphs to compute `glyf` and `loca` sizes.
4. Decides short vs long loca format.
5. Builds generated table-directory entries with placeholder checksum handling.
6. Writes the sfnt header, sorted directory, copied tables, generated glyph/location data, generated support tables, and final `head`.

Public entry points:
- `psf_write_truetype_font`
- `psf_write_truetype_stripped`
- `psf_write_cid2_font`
- `psf_write_cid2_stripped`

Notable constraints and risks:
- Several comments state checksums are not computed for generated tables.
- The subset writer does not trim `maxp`/related metrics tables to the subset, because that would require broader table rewriting.
- `MAX_NUM_TABLES` limits output tables to 40.
- Generated `OS/2` range bits are adjusted for symbolic/private-use biased fonts.
