# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fonts.c

Generic font translation logic. It maps Word font numbers/styles to Antiword output font names, then prunes unused entries.

Core state:

- `tFontTableRecords`
- `pFontTable`, an array of `font_table_type`

Main responsibilities:

- Lookup:
  - `iGetFontByNumber()`
  - `szGetOurFontname()`
  - `iFontname2Fontnumber()`
  - `pGetNextFontTableRecord()`
  - `tGetFontTableLength()`
- Default selection:
  - `szGetDefaultFont()` maps Word pitch/family/emphasis to serif, sans-serif, or monospaced defaults.
- Translation-table parsing:
  - `bReadFontFile()` reads CSV-style font mapping records from the platform-specific fontnames file.
  - `bFontEqual()` compares Word font names case-insensitively, handling one-byte and two-byte Unicode-style strings.
  - `vFontname2Table()` writes matching Word/local font mappings into a `font_table_type`.
- Table creation:
  - `vCreate0FontTable()` handles Word for DOS with synthetic Courier/Times mapping.
  - `vCreate2FontTable()` handles WinWord 1/2 font tables, including three implicit fonts for Word 1.
  - `vCreate6FontTable()` parses Word 6/7 FFN records and optional alternate names.
  - `vCreate8FontTable()` parses Word 8/9/10 Unicode FFN records from OLE streams.
- Cleanup and correction:
  - `vMinimizeFontTable()` marks fonts actually used by font records and stylesheet-derived fonts, compacts unused entries, and ensures `TABLE_FONT` exists.
  - `vDestroyFontTable()` frees the table.
  - `vCorrectFontTable()` restricts PDF output to built-in PDF fonts and maps Cyrillic PS to monospaced fonts.
  - `lComputeSpaceWidth()` delegates to platform-specific string-width logic.

The file is central to output fidelity. It interacts with property parsers, stylesheet lists, font lists, OLE stream reading, output encodings, and platform-specific font opening in `fonts_u.c`/`fonts_r.c`.
