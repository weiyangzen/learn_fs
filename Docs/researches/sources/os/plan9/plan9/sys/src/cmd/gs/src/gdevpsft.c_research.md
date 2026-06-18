# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsft.c

This file writes embedded TrueType/sfnt data from Ghostscript Type 42 and CIDFontType 2 fonts. It can write normal TrueType subsets, stripped TrueType fonts, CIDFontType 2 fonts, and stripped CIDFontType 2 fonts.

Core responsibilities:
- Read and filter the source sfnt table directory through `pfont->data.string_proc`.
- Copy existing tables while omitting/replacing tables that must be synthesized (`glyf`, `loca`, selected generated cmap/name/OS/2/post/metrics tables).
- Rebuild `glyf` and `loca` from selected glyph outlines.
- Generate Macintosh and Windows cmap subtables when requested or required.
- Generate `name`, `OS/2`, metrics (`hmtx`/`vmtx`), and `post` tables when absent or requested.
- Sort the final table directory and write a complete sfnt header and table directory.
- Expand subset glyphs with composite pieces through `psf_add_subset_pieces` before writing Type 42 subsets.

Important helper groups:
- Big-endian table writers: `put_ushort`, `put_ulong`, `put_loca`, `put_u16`, and `put_u32`.
- Safe table copying: `write_range` repeatedly calls `string_proc` and handles segmented font data by shrinking reads.
- Generated cmap support: `write_cmap_0`, `write_cmap_6`, `write_cmap`, and `size_cmap`.
- Metrics support: `size_mtx` computes compact metric-table length and `write_mtx` emits widths and side bearings.
- Name/OS2/post support: `write_name`, `write_OS_2`, `update_OS_2`, `compute_post`, and `write_post`.

The main implementation, `psf_write_truetype_data`, scans existing tables, captures `head` and `maxp`, computes glyph and loca sizes, chooses short or long `loca`, builds generated table records with placeholder checksums, writes copied tables, emits generated glyph/location/support tables, and finally writes the corrected `head` table.

Plan 9-specific robustness changes are visible in `limdbl2ushort` and `limdbl2long`, which clamp floating-point metric conversions to avoid exceptions when large doubles are stored into integer fields.

Public entry points:
- `psf_write_truetype_font`
- `psf_write_truetype_stripped`
- `psf_write_cid2_font`
- `psf_write_cid2_stripped`

Notable constraints and risks:
- Comments explicitly say generated table checksums are not computed.
- Subset fonts do not trim `maxp`/related tables down to the highest used glyph because doing so would require broad table rewriting.
- `MAX_NUM_TABLES` limits output to 40 table records.
- Generated cmap handling uses private-use bias `0xf000` by default and may adjust OS/2 range bits for symbolic/private-use output.
