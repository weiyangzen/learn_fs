# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscedata.c

## Role

`gscedata.c` is a generated data file containing compact tables for Ghostscript’s built-in glyph encodings. It is generated from PostScript encoding files by `toolbin/encs2c.ps`.

This is font encoding data, not filesystem code.

## Generation Inputs

The file states it was generated from:

- `gs_std_e.ps`
- `gs_il1_e.ps`
- `gs_sym_e.ps`
- `gs_dbt_e.ps`
- `gs_wan_e.ps`
- `gs_mro_e.ps`
- `gs_mex_e.ps`
- `gs_mgl_e.ps`
- `gs_lgo_e.ps`
- `gs_lgx_e.ps`
- `gs_css_e.ps`

## Core Data Model

Glyph names are stored once in `gs_c_known_encoding_chars[]`, grouped by glyph-name length. Encodings store compact `ushort` values created by:

- `N(len, offset)`

The companion header defines:

- lower `NUM_LEN_BITS` bits as name length
- remaining bits as offset within the length group

This allows compact glyph-name lookup without storing pointers per glyph.

## Exported Constants

- `gs_c_known_encoding_total_chars = 5483`
- `gs_c_known_encoding_max_length = 19`
- `gs_c_known_encoding_count = 11`

## Exported Offset Table

`gs_c_known_encoding_offsets[]` contains per-name-length starting offsets:

`0, 0, 52, 104, 404, 876, 1081, 1771, 2072, 2272, 2776, 3116, 3754, 4414, 4830, 5250, 5280, 5360, 5428, 5464, 5483`

These offsets support lookup by glyph-name length.

## Encoding Tables

Defines 11 static encoding tables and 11 reverse tables:

- `gs_c_known_encoding_0` / reverse: `StandardEncoding`
- `gs_c_known_encoding_1` / reverse: `ISOLatin1Encoding`
- `gs_c_known_encoding_2` / reverse: `SymbolEncoding`
- `gs_c_known_encoding_3` / reverse: `DingbatsEncoding`
- `gs_c_known_encoding_4` / reverse: `WinAnsiEncoding`
- `gs_c_known_encoding_5` / reverse: `MacRomanEncoding`
- `gs_c_known_encoding_6` / reverse: `MacExpertEncoding`
- `gs_c_known_encoding_7` / reverse: `MacGlyphEncoding`
- `gs_c_known_encoding_8` / reverse: `AdobeLatinOriginalGlyphEncoding`
- `gs_c_known_encoding_9` / reverse: `AdobeLatinExtensionGlyphEncoding`
- `gs_c_known_encoding_10` / reverse: `CFFStandardStrings`

## Exported Pointer Tables

- `gs_c_known_encodings[]`: points to the 11 forward encoding arrays, then terminates with `0`.
- `gs_c_known_encodings_reverse[]`: points to the 11 reverse arrays, then terminates with `0`.

## Exported Length Tables

Forward lengths:

`256, 256, 256, 256, 256, 256, 256, 258, 229, 86, 379, 0`

Reverse lengths:

`149, 205, 189, 188, 224, 208, 165, 257, 228, 86, 378, 0`

## Important Semantics

- `.notdef` is represented repeatedly as `N(7,0)`.
- Forward arrays map character codes or glyph-set indices to compact glyph-name IDs.
- Reverse arrays map sorted glyph-name IDs back to character codes or glyph-set indices. `gscencs.c` binary-searches these arrays.
- Encoding 7 (`MacGlyphEncoding`) has 258 entries, so not every table is byte-sized.
- Encoding 10 (`CFFStandardStrings`) has 379 entries.

## Dependencies

- Includes `stdpre.h`, `gstypes.h`, and `gscedata.h`.
- Depends on `ushort` and the `N(...)` macro from `gscedata.h`.

## Notable Risks

- Generated file should not be manually edited unless the generator and consumers are kept consistent.
- Reverse tables must remain sorted in the order expected by `gs_c_decode`.
