# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/parse.c

This file parses wiki source text into a linked list of `Wpage` nodes.

Node creation:
- `mkwtxt` allocates a `Wpage` with type and text.
- `freepage` is in `io.c`, but this parser uses it when condensing.

Text normalization:
- `strcondense` collapses whitespace runs to one space and trims leading/trailing whitespace.
- `wcondense` condenses `Wplain` text and merges adjacent `Wplain` nodes.

Inline parsing:
- `mklink` parses `[text]` or `[text|url]` link bodies.
- `wlink` scans plain nodes for bracketed links and splits nodes around them.
- `findmanref` finds `name(section)` references where section is one digit.
- `wman` splits plain nodes around manpage references.
- `isheading` treats a line as heading if it has uppercase runes and no lowercase runes.

Block parsing in `Brdpage`:
- Blank lines create paragraph separators.
- `*` starts a bullet plus plain text.
- `!` starts preformatted text; optional following space is skipped.
- More than four `-` characters forms a horizontal rule.
- All-uppercase lines become headings.
- Other lines become plain text.

Post-processing:
- After reading all lines, parser condenses plain text, splits links, then splits man references.
- Empty pages set error `"empty page"`.

Debug:
- `printpage` dumps parsed node types and text/url/section values.

Role:
- This is the wiki markup front end used by history parsing and page writes.
