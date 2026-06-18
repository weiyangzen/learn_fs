# File Research: sources/os/plan9/9front/sys/src/cmd/aux/wikifmt.c

Implements a Google Code wiki syntax to HTML converter.

Key responsibilities:
- Reads all input into a growable buffer and writes buffered HTML to stdout.
- Parses headings, links/images, inline code, bold/italic/sup/sub/strike, preformatted/teletype blocks, tables, blockquotes, lists, horizontal rules, comments, and raw-looking HTML tags.
- Escapes `<`, `>`, and `&` in content contexts.
- Generates anchor names for headings.
- Handles automatic links for `http://`, `https://`, and `ftp://`.
- Uses recursive `body` parsing with global state for quote/list/table indentation.

Important interfaces:
- Standalone command with optional input file argument.
- Uses Plan 9 libc only.

Notes:
- Image detection is based on URL suffix `.png`, `.jpg`, or `.gif`.
- The parser is stateful and hand-rolled, not a general HTML sanitizer.
