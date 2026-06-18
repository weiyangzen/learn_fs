# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/parse.c

Wiki markup parser that converts raw wiki text lines into linked `Wpage` nodes.

Key behavior:
- `Brdpage()` reads lines from a caller-supplied line reader and emits typed page nodes: paragraph breaks, headings, bullets, links, man-page references, plain text, preformatted lines, and horizontal rules.
- Whitespace is condensed for non-preformatted content.
- Runs of adjacent plain text are merged by `wcondense()`.
- Bracketed links are parsed as `[text]` or `[text | url]`.
- Man references like `name(1)` are detected inside plain text and converted to `Wman`.
- Headings are inferred from all-uppercase text containing at least one uppercase rune and no lowercase runes.
- `printpage()` dumps parsed node types for debugging.

Notable dependencies:
- Plan 9 String/Bio/rune helpers and allocation/free helpers from `wiki.h`.

Research notes:
- Link and man-reference parsing mutate intermediate strings, then duplicate the pieces into new nodes.
- Preformatted lines start with `!`; a following space is stripped.
