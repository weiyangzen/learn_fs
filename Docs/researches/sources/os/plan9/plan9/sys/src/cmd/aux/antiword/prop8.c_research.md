# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop8.c

This file parses Word 8/9/10/11, Word 97 through Word 2003, property streams and builds Antiword’s internal document metadata lists.

Key behavior:
- Reads Word table-stream records through big-block or small-block depots depending on stream size.
- Extracts document properties, section descriptors, header/footer offsets, list definitions, paragraph properties, table row bounds, character/font runs, and picture references.
- Decodes Word 8 SPRM/grpprl records by opcode class and applies recognized properties to `document_block_type`, `section_block_type`, `row_block_type`, `style_block_type`, `font_block_type`, and `picture_block_type`.
- Builds downstream lists via `vCreateDocumentInfoList`, `vAdd2SectionInfoList`, `vCreat8HdrFtrInfoList`, `vAdd2ListInfoList`, `vAdd2StyleInfoList`, `vAdd2RowInfoList`, `vAdd2FontInfoList`, and `vAdd2PictInfoList`.

Important details:
- `iGet8InfoLength()` is the local SPRM length decoder and has special handling for tab-change opcode `0xc615`.
- Table row detection combines explicit table flags and row-end table definition data.
- Word 8 list data is split between LFO, LSTF, LVLF, PAPX, CHPX, and XString records.
- Character property parsing rejects OLE objects as pictures and maps picture offsets through the Data stream.

Filesystem relevance:
- Indirect but important: this is binary document/container metadata parsing on top of OLE stream block reads.
