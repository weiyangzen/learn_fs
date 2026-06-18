# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/properties.c

Central dispatcher for building document property lists across supported Word versions.

Key responsibilities:
- `vGetPropertyInfo()` selects the correct parser set for Word for DOS, WinWord 1/2, Word 6/7, and Word 8.
- Builds stylesheet, DOP, section, paragraph, header/footer, character, font table, list, and summary metadata as needed.
- Avoids expensive character/font/image parsing for output modes that do not need it.
- Calls `vCorrectFontTable()` after parsing to normalize font mappings for the chosen conversion and encoding.
- `ePropMod2RowInfo()` translates a stored property modifier into table row/cell information for Word 2, 6/7, or 8.

Dependencies:
- Version-specific property parsers (`prop0`, `prop2`, `prop6`, `prop8`), summary readers, font table builders, option state, and property modifier storage.

Research relevance:
- This is the conversion pipeline’s property ingestion coordinator.
