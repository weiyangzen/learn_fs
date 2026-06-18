# File Research: sources/os/plan9/9front/sys/src/cmd/dict/pcollins.c

Adapter for “Paperback Collins” dictionaries using `>tag<` markup.

Key elements:
- Defines internal formatting tokens for bold, headword start/end, italics, pronunciation start/end, and roman text.
- `normtab` translates 7-bit source bytes to runes or tag sentinels.
- `tagtab` maps Collins tags to runes, accents, ligatures, or control tokens.
- `pcollprintentry` supports raw mode, headword-only mode, accent ligature combining, multi-rune expansions, pronunciation suppression, and headword boundaries.
- `pcollnextoff` finds entries beginning with `>H<`.
- `gettag` parses tag names between `>` and `<`.

Dependencies:
- Uses common ligature/multi-rune utilities and output helpers.

Research notes:
- Used for French, Italian, Spanish, and related Collins dictionaries in `dicts[]`.
- Pronunciation content is currently suppressed because the key is incomplete.
