# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop6.c

Word 6/7 property extractor for compound-document table stream properties, sections, headers/footers, paragraph/table data, character formatting, and pictures.

Key responsibilities:
- Implements `iGet6InfoLength()` for Word 6/7 SPRM/property record traversal.
- Reads DOP data from the WordDocument stream through the big block depot.
- Parses section PLCF/SEPX data, including outline numbering descriptors, page-break behavior, header/footer specification, and list-level flags.
- Builds header/footer character-position lists.
- Parses paragraph FKPs from big-block reads, fills styles from stylesheets, applies paragraph SPRMs, and converts character positions to file offsets/list IDs.
- Detects table cells, row ends, borders, and column widths.
- Applies detailed character SPRMs for revision deletion, plain/default formatting, bold/italic/strike/caps/hidden, font number, underline, size, color, sub/superscript, and size deltas.
- Extracts picture references from `fcPic` while rejecting OLE objects and converts data positions to file offsets.

Dependencies:
- Uses compound-file block depot reads, FIB offsets, stylesheet helpers, character-position mapping, and shared document/section/header/style/font/row/picture list APIs.

Notable risks:
- Static SPRM length tables must match Word 6/7 binary format exactly.
- Several unsupported or partially handled SPRMs are logged only in debug paths.
- The parser trusts FKP run counts and offset arithmetic after basic bounds checks.
