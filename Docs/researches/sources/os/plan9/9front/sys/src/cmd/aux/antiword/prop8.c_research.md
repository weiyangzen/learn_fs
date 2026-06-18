# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop8.c

Word 8/9/10/11 property parser for Word 97 through Word 2003 binary documents.

Key responsibilities:
- Decodes Word 8 SPRM/property record lengths with `iGet8InfoLength()`.
- Reads table-stream data from either the big block depot or small block depot.
- Extracts DOP document properties: header/footer flags, default tab width, creation and revision dates.
- Parses section PLCF/SEPX data, page-break behavior, header/footer specifications, outline numbering descriptors, and header/footer character positions.
- Parses Word 8 list structures (`LFO`, `LSTF`, `LVLF`) into Antiword list records.
- Parses paragraph FKPs into style records and table row records.
- Parses character FKPs into font records and picture references.

Important behavior:
- `vGet8LstInfo()` runs before paragraph/style parsing so list references can be resolved while interpreting paragraph SPRMs.
- `vGet8PapInfo()` combines stylesheet defaults with paragraph-specific SPRMs, maps character positions to file offsets/list IDs, and records table rows.
- `eGet8RowInfo()` detects table cells/end-of-row from `fInTable`, `fTtp`, sub-table flags, borders, and `sprmTDefTable`.
- `vGet8FontInfo()` handles revision deletion, bold/italic/strike/caps/hidden, underline, color, superscript/subscript, font size, font number, and reset/plain operations.
- `bGet8PicInfo()` recognizes `fcPic` references while rejecting OLE objects.

Dependencies:
- OLE PPS/block-depot readers, text/data block mapping, stylesheet/list/font/row/picture/header-footer list APIs, Word character-position conversion helpers.

Notable risks:
- Binary offsets and SPRM lengths must exactly match Word’s file format.
- Several unsupported or diagnostic-only SPRMs are logged rather than fully interpreted.
- Table/list parsing has explicit corruption guards, but still relies heavily on well-formed FKP/page structures.
