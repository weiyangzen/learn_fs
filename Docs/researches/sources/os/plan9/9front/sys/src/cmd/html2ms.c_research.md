# File Research: sources/os/plan9/9front/sys/src/cmd/html2ms.c

Implements a standalone loose HTML parser that emits `ms`/`tbl` roff markup.

Key points:
- Defines lightweight `Tag`, `Attr`, `Text`, and `Table` structures for parsing and output state.
- Maintains output buffer growth, rune emission, line position, whitespace collapsing, preformatted mode, font style, font size, and hidden-output state.
- Converts common HTML tags:
  - paragraphs/headings/lists/br/hr/pre to `.LP`, `.SH`, `.IP`, `.br`, `.DS/.DE`
  - emphasis/bold/code/small/big/sub/sup to font/size/vertical roff escapes
  - quotes to `.QS/.QE` or `.QP`
  - tables to `.TS/.TE` with generated cell formats and `T{...T}` enclosure
- Implements a small class/style recognizer for spans (`bold`, `italic`, `subscript`, `superscript`, and `text-align: center`).
- Skips or self-closes metadata, head, style, script, link, meta, and image-like content.
- Parses comments, CDATA-ish blocks, attributes with quoted or unquoted values, tags, HTML entity basics, UTF-8 runes, and text.
- Escapes leading `.` and backslashes so generated roff remains safe.
- Handles nested tables by flattening inner table cells into the nearest outer table.

Dependencies and interactions:
- Uses Plan 9 `Biobuf`, UTF/Rune helpers, ctype, and libc.
- Does not depend on Plan 9 `<html.h>`; it implements parsing itself.

Research relevance:
- This is a purpose-built converter from HTML-ish input to Plan 9 roff/ms output, useful for understanding text-conversion tooling outside filesystem code.
