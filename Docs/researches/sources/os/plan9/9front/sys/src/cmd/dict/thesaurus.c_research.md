# File Research: sources/os/plan9/9front/sys/src/cmd/dict/thesaurus.c

Adapter for Collins Thesaurus data.

Key elements:
- `thesprintentry` handles compact markup characters: `*` control sequences, `#` accent encodings, and suppression of selected markers.
- Headword mode stops after the leading lexical section.
- Raw mode writes bytes directly.
- `thesnextoff` locates next entries beginning with `*L`.
- `thesprintkey` reports no key.

Dependencies:
- Uses common output helpers.

Research notes:
- Accent handling is table-based for vowels and cedilla cases embedded as `#` sequences.
