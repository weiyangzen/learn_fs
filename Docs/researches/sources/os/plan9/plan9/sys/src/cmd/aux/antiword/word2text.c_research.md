# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/word2text.c

This file is Antiword’s main Word-to-output rendering pipeline.

Key behavior:
- Initializes a document, reads options, prepares headers/footers and notes, and emits through the selected output backend.
- Walks text, footnote, endnote, text-box, and header text-box lists.
- Applies style, font, list, section, table-row, hidden-text, deletion-mark, image, note, tab, and page-break state while reading characters.
- Converts list numbers, bullets, roman numerals, alphabetic counters, notes, images, and tables into output records.
- Provides separate decryptors for header/footer output and XML footnote text.

Important details:
- Output is accumulated as a doubly linked list of `output_type` fragments, split and justified when width limits are exceeded.
- Table rows temporarily switch to a fixed table font and are rendered via `vTableRow2Window()`.
- Embedded Word control ranges are skipped between `START_EMBEDDED` and `END_IGNORE`/`END_EMBEDDED`.
- The pipeline frees all document-global lists through `vFreeDocument()` after conversion.

Filesystem relevance:
- Central consumer of parsed file streams; output writing is delegated to backend functions.
