# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfsfnt.h

Purpose: sfnt/TrueType table structure and constant definitions.

Key contents:
- Includes `stdint_.h` and defines exact-size TrueType aliases (`uint8`, `int16`, `uint32`, etc.).
- Defines `BigDate`, `sfnt_DirectoryEntry`, `sfnt_OffsetTable`, header flags, and sfnt constants.
- Defines structures for font header, horizontal/vertical metrics headers, max profile, glyph metrics, cmap directory/platform entries, name records, naming table, device metrics, PostScript info, subheaders, and font table info.
- Defines outline flag bits (`ONCURVE`, `XSHORT`, `YSHORT`, `REPEAT_FLAGS`, coordinate flags).
- Defines component glyph flags (`ARG_1_AND_2_ARE_WORDS`, `ARGS_ARE_XY_VALUES`, scaling flags, `MORE_COMPONENTS`, `WE_HAVE_INSTRUCTIONS`, `USE_MY_METRICS`).
- Defines platform enums and reversed four-character table tags for this code’s integer representation.
- Defines `RAW_TRUE_TYPE_SIZE`.

Dependencies: `stdint_.h`.

Integration notes: parsed by `ttfmain.c` and helper code through offsets and flag constants.

Risks: several structs describe on-disk layouts but parsing in this code uses explicit big-endian reader functions rather than direct struct casts; direct casting would be unsafe across alignment/endian differences.
