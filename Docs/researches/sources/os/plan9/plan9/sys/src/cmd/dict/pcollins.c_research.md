# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/pcollins.c

Implements dictionary callbacks for the Paperback Collins French/Spanish/Italian-style format, where tags are delimited by `>` and `<`.

`tagtab` maps short formatting/character tags to literal runes, ligature accent codes, multi-rune codes, or control states: `H` starts headword, `X` ends headword, `[`/`{` start pronunciation suppression, and `]` ends it. `normtab` maps input bytes to runes and marks `>` as tag start.

`pcollprintentry` streams an entry, optionally raw (`cmd == 'r'`) or headword-only (`cmd == 'h'`). It buffers the previous rune so accent tags can combine through `liglookup`, expands multi-rune tags via `multitab`, suppresses pronunciation text, and inserts line breaks or `.  ` after headword close in normal output.

`pcollnextoff` seeks forward line by line until it finds a line beginning `>H<`, the format’s entry/headword marker. `pcollprintkey` reports that no pronunciation key is implemented.

Integration points: registered by `utils.c` for Collins French, Italian, and Spanish dictionaries. It uses shared `lookassoc`, `changett`, `out*`, and ligature/multi-rune helpers.

Risks and notes: tag text is read into a fixed 1000-byte buffer and unknown tags are ignored except debug diagnostics. Pronunciation is intentionally hidden because the key is not understood.
