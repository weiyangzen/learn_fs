# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop2.c

WinWord 1/2 property extractor for document properties, sections, headers/footers, paragraph/table metadata, character formatting, and pictures.

Key responsibilities:
- Implements `iGet2InfoLength()` for skipping WinWord 1/2 SPRM/property records.
- Reads DOP data for header/footer specification, default tabs, and created/revised DTTM dates.
- Parses section PLCF/SEPX data and header/footer character-position tables.
- Parses paragraph FKPs, style changes, indentation, spacing, list numbering fields, and table row/cell metadata.
- Detects row boundaries and border/column definitions for table output.
- Applies WinWord 1 and WinWord 2 CHPX character formatting variants to stylesheet-derived font records.
- Extracts picture offsets from character properties and registers them in the picture list.

Dependencies:
- Uses FIB offsets for WinWord 1/2, 512-byte FKPs, stylesheet helpers, row/picture/font/style list APIs, and direct file reads.

Notable risks:
- Property-length decoding is central; a wrong SPRM length desynchronizes parsing.
- Picture offsets are bounded by a hard-coded 32 MiB maximum.
- Table-state detection is heuristic over `fInTable`, `fTtp`, and table-definition properties.
