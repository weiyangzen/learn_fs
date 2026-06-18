# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/xml.c

This file implements Antiword's DocBook/XML output backend.

Key behavior:
- Maintains a DocBook tag stack for `book`, `chapter`, `sectN`, `para`, tables, lists, emphasis, footnotes, and inline super/subscript.
- Escapes XML-sensitive characters and emits UTF-8 converted special characters through Antiword's character translation layer.
- Builds book metadata from Word document properties: title, subject, author, date, company, and language.
- Converts Word paragraphs, headings, lists, page breaks, tables, and footnote markers into DocBook structures.
- Tracks output state globally, including open paragraph/list/table/header levels and current table column count.

Important details:
- Empty Word headings and lists are patched with empty DocBook paragraphs/items because DocBook disallows empty structural elements.
- Tables are emitted as `informaltable` with `tgroup`, `colspec`, `tbody`, `row`, and `entry`.
- List style codes are mapped to DocBook ordered/itemized list attributes.
- Footnote insertion temporarily closes super/subscript tags and restores them after the footnote.

Filesystem relevance:
- Indirect: document conversion output layer; consumes parsed Word/OLE content but does not implement filesystem behavior.
