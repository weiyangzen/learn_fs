# File Research: sources/os/plan9/9front/sys/src/cmd/dict/oed.c

Oxford English Dictionary SGML-like markup adapter.

Key elements:
- Large tag table maps OED element names to semantic handlers for entries, variants, headwords, pronunciations, etymology, quotes, senses, tables, Greek, subscript/superscript, and related formatting.
- Large special-character table maps entity names to Unicode runes, internal accent ligatures, or multi-rune expansions.
- Translation tables support normal text, phonetic text, Greek text, subscript, and superscript.
- `oedprintentry` scans the raw entry byte-by-byte, translates entities and tags, handles nested translation tables with `changett`, and formats headwords/senses/statuses.
- `oednextoff` locates entries beginning with `<e>`, `<ve>`, or those tags with attributes.
- `oedprintkey` emits a built-in pronunciation key.
- `getspec` parses `&name.` special entities; `gettag` parses `<tag aux=value>` and end tags.
- `dostatus` renders selected status attributes such as obsolete and alternate forms.

Dependencies:
- Uses `dict.h` private-use tokens, ligature helpers, output helpers, and binary association lookup.
- Runtime depends on OED data and index paths declared in `utils.c`.

Research notes:
- Unknown tags/entities/statuses are only reported in debug mode.
- Several special-character mappings are approximate, and the file documents names without close Unicode equivalents.
