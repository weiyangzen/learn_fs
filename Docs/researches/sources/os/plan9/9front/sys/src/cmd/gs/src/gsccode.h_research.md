# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsccode.h

## Role

`gsccode.h` defines Ghostscript character-code and glyph-code types plus encoding and glyph-space enums.

This is font/text infrastructure, not filesystem code.

## Main Types

- `gs_char`: unsigned long character code. Composite fonts require at least 32 bits.
- `gs_glyph`: unsigned long glyph identifier.
- `gs_encoding_index_t`: known encoding index enum.
- `gs_glyph_space_t`: selector for name/index/no-generation glyph spaces.
- `gs_glyph_mark_proc_t`: GC marking callback for glyphs.
- `gs_glyph_name_proc_t`: callback to map a glyph code to a string name.

## Glyph Code Space

`gs_glyph` is partitioned into ranges:

- `GS_NO_GLYPH`: unknown glyph identity.
- Values below `GS_MIN_CID_GLYPH`: named glyphs.
- Values from `gs_c_min_std_encoding_glyph` up to `GS_MIN_CID_GLYPH`: private built-in encoding glyph names managed by `gscencs.h`.
- Values from `GS_MIN_CID_GLYPH` to `GS_MIN_GLYPH_INDEX`: CIDs.
- Values at or above `GS_MIN_GLYPH_INDEX`: glyph indices.

## Known Encodings

The enum defines 11 known encodings:

- Real encodings:
  - `StandardEncoding`
  - `ISOLatin1Encoding`
  - `SymbolEncoding`
  - `DingbatsEncoding`
  - `WinAnsiEncoding`
  - `MacRomanEncoding`
  - `MacExpertEncoding`
- Pseudo-encodings/glyph sets:
  - `MacGlyph`
  - `AdobeLatinOriginalGlyph`
  - `AdobeLatinExtensionGlyph`
  - `CFFStandardStrings`

`NUM_KNOWN_REAL_ENCODINGS` is 7, and `NUM_KNOWN_ENCODINGS` is 11.

## Constants

- `GS_NO_CHAR`
- `GS_NO_GLYPH`
- `GS_MIN_CID_GLYPH`
- `GS_MIN_GLYPH_INDEX`
- `GS_GLYPH_TAG`
- `GS_MAX_GLYPH`

Backward-compatible lowercase aliases are also provided.

## Dependencies

- Uses `ulong`, `bool`, `gs_memory_t`, and `gs_const_string`, which must be available from the broader Ghostscript include context.

## Notable Risks

- Client code must not mix built-in-encoding private glyph values with global-name glyph values.
- The exact numeric partition depends partly on `arch_sizeof_long`.
