# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/xml.c

Role: Antiword output backend that emits DocBook-style XML from Word document text/layout events. It is not a filesystem file, but it is part of the 9front aux userland source tree in scope.

Core structures and state:
- Maintains a global XML tag stack (`aucStack`, `tStacksize`, `tStackNextFree`) and DocBook tag table mapping numeric tags to names and newline behavior.
- Tracks open formatting and structural state through globals: encoding, Word version, old-Mac mode, emphasis/superscript/subscript/title/table/footnote flags, paragraph/list/header levels, table column count, and footnote number.
- Uses `diagram_type` output state, especially `pOutFile` and `lXleft`, as the sink interface.

Main behavior:
- `vPrologueXML` initializes conversion state and the tag stack from `options_type`.
- `vCreateBookIntro` writes `<book>`, optional language attribute, title, and `<bookinfo>` metadata from document properties.
- `vPrintXML`, `vSubstringXML`, `vPrintSpecialChar`, and `vPrintChar` handle text, XML escaping, character-set conversion, footnote references, and inline style transitions.
- `vStartOfParagraphXML`, `vEndOfParagraphXML`, `vSetHeadersXML`, list functions, and table functions translate Word layout events into legal DocBook nesting.
- `vEpilogueXML` closes all tags up to `book` and frees the stack.

Important invariants:
- Tag ordering is enforced by stack push/pop helpers; mismatches are fatal/debug-diagnosed.
- Empty Word constructs that DocBook disallows are filled with empty `<para/>` or list item/paragraph combinations before closing.
- Tables cannot currently contain lists; lists in tables are skipped or tables are ended first.

Dependencies and integration:
- Relies heavily on Antiword helpers from `antiword.h`: metadata accessors, `ulTranslateCharacters`, UTF-8 conversion, style tests, list/table constants, and diagnostic macros.
- Emits directly to `FILE *`, not through Plan 9 9P abstractions.
