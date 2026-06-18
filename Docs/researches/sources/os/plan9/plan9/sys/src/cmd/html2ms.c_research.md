# File Research: sources/os/plan9/plan9/sys/src/cmd/html2ms.c

Lightweight HTML-to-ms/troff converter.

- Reads HTML-like input from stdin and writes ms/troff macros to stdout.
- Uses a tag dispatch table (`Goobie`) mapping many HTML tags to actions or ignores.
- Handles headings, paragraphs, line breaks, horizontal rules, lists, display/pre blocks, font changes, definition-list terms, and table start/end markers.
- Maintains font and list stacks of fixed depth `SSIZE`.
- Decodes a local table of common HTML entities plus numeric ASCII printable entities.
- Collapses whitespace outside `<pre>` and emits newlines/macro starts carefully for troff formatting.

Dependencies are Plan 9 `bio`, `ctype`, and libc.

Notable concerns: this is not a full HTML parser. Tag/attribute parsing is simple, entity buffer is only 8 bytes, and many tags are ignored or only minimally represented.
