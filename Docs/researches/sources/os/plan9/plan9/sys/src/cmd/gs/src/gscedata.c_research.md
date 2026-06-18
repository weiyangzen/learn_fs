# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscedata.c

Generated compact data tables for Ghostscript built-in encodings.

Generation/source:
- Generated mechanically by `toolbin/encs2c.ps`.
- Source encoding files listed in the header include:
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
- Includes `stdpre.h`, `gstypes.h`, and `gscedata.h`.

Key data:
- `gs_c_known_encoding_chars[]`: packed sorted glyph-name character storage.
- `gs_c_known_encoding_total_chars = 5483`.
- `gs_c_known_encoding_max_length = 19`.
- `gs_c_known_encoding_offsets[]`: offset table by glyph-name length.
- `gs_c_known_encoding_count = 11`.
- Per-encoding forward tables:
  - `gs_c_known_encoding_0`: StandardEncoding, length 256
  - `gs_c_known_encoding_1`: ISOLatin1Encoding, length 256
  - `gs_c_known_encoding_2`: SymbolEncoding, length 256
  - `gs_c_known_encoding_3`: DingbatsEncoding, length 256
  - `gs_c_known_encoding_4`: WinAnsiEncoding, length 256
  - `gs_c_known_encoding_5`: MacRomanEncoding, length 256
  - `gs_c_known_encoding_6`: MacExpertEncoding, length 256
  - `gs_c_known_encoding_7`: MacGlyphEncoding, length 258
  - `gs_c_known_encoding_8`: AdobeLatinOriginalGlyphEncoding, length 229
  - `gs_c_known_encoding_9`: AdobeLatinExtensionGlyphEncoding, length 86
  - `gs_c_known_encoding_10`: CFFStandardStrings, length 379
- Per-encoding reverse lookup tables:
  - reverse lengths are 149, 205, 189, 188, 224, 208, 165, 257, 228, 86, and 378.
- Publishes pointer vectors:
  - `gs_c_known_encodings[]`
  - `gs_c_known_encodings_reverse[]`
- Publishes length vectors:
  - `gs_c_known_encoding_lengths[]`
  - `gs_c_known_encoding_reverse_lengths[]`

Important implementation notes:
- Values are encoded with `N(len, offset)`, defined in `gscedata.h`, packing a glyph-name length and offset into a `ushort`.
- Forward encoding tables map character codes to packed glyph-name identifiers.
- Reverse tables map sorted glyph identifiers back to character codes for binary-search decode in `gscencs.c`.
- This file is pure generated data; manual edits should be avoided unless the generator and source encoding files are updated consistently.
