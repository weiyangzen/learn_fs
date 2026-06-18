# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/thesaurus.c

Implements callbacks for Collins Thesaurus data.

`thesprintentry` streams records and interprets a compact markup. Raw mode emits bytes unchanged. `*L` marks headword records; in headword mode, non-`L` starred sections terminate output, while in normal mode `*L` starts a new line. `*S` emits a parenthesized single-character sense marker. `#` escapes accented vowels and cedilla variants by selecting from fixed strings. `+` and `<` are dropped. A space before `*` ends headword output.

`thesnextoff` scans for the next line starting `*L`. `thesprintkey` reports no key.

Integration points: registered as `thesaurus` in `utils.c`.

Risks and notes: accent escape handling only covers a small hard-coded set and indexes `0..4`. Unrecognized markup is mostly skipped or emitted literally.
