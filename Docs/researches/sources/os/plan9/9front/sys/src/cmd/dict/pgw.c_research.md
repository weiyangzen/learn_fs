# File Research: sources/os/plan9/9front/sys/src/cmd/dict/pgw.c

Project Gutenberg Webster dictionary adapter.

Key elements:
- Similar architecture to `oed.c`, but for PGW HTML/SGML-like tags and semicolon-terminated entities.
- Tag table handles headwords, paragraphs, definitions, senses, parts of speech, bold/italic, blockquote, breaks, and cross-reference-like markup.
- Special-character table maps HTML-like entity names to Unicode or internal ligature/multi-rune tokens.
- Translation tables support normal, phonetic, Greek, subscript, and superscript text.
- `pgwprintentry` translates source bytes/entities/tags and formats headword or full entry output.
- `pgwnextoff` finds entries beginning with `<p><hw>` or a fallback `<p>{` pattern.
- `pgwprintkey` emits the same built-in pronunciation key structure as OED.
- `getspec` parses `&name;`; `gettag` parses tag names.

Dependencies:
- Uses `dict.h` sentinels, common lookup/output/ligature utilities.

Research notes:
- Thanks comment credits Caerwyn Jones for the module.
- Several entity mappings are approximate and documented inline.
