# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fonts.c

This file implements generic font translation table construction and lookup across Word versions.

Key routines:
- Lookup/accessors: `iGetFontByNumber`, `szGetOurFontname`, `iFontname2Fontnumber`, `pGetNextFontTableRecord`, `tGetFontTableLength`.
- Matching/defaulting: `szGetDefaultFont`, `bFontEqual`, `vFontname2Table`.
- Table lifecycle: `vCreateFontTable`, `vMinimizeFontTable`, `vDestroyFontTable`.
- Font table readers: `vCreate0FontTable`, `vCreate2FontTable`, `vCreate6FontTable`, `vCreate8FontTable`.
- Output corrections: `vCorrectFontTable`, with PDF default-font restriction and Cyrillic PostScript monospaced fallback.
- Metrics helper: `lComputeSpaceWidth`.

Important behavior:
- Internal table has four style entries per Word font: regular, bold, italic, bold+italic.
- Reads the external font translation file line-by-line as `Word font, italic, bold, local font, special`.
- Word 8/97+ font tables are read from the table stream using SBD or BBD depending on stream size.
- `vMinimizeFontTable` keeps only fonts used by font runs or potentially used by styles, and ensures the table font exists.

Dependencies:
- Font-info list, style-info list, stylesheet font filling, OLE stream readers, Unicode copy helpers, font table file opener, and platform-specific width/open-font backends.

Role in antiword:
- Converts Word font identifiers and names into antiword/local output font names, then trims and corrects that table for output format constraints.
