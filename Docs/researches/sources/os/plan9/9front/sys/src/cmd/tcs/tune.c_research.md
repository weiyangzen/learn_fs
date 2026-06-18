# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/tune.c

`tune.c` implements conversion between Unicode Tamil code points and TUNE private-use encoded Tamil glyph sequences.

Main data:
- `t1[]`: independent Tamil vowels and aytham to TUNE private-use code points.
- `t2[]`: Tamil vowel signs/virama indexed by low nibble positions.
- `t3[]`: Tamil consonant bases to TUNE base forms.

Core functions:
- `findbytune()`, `findbyuni()`, `findindex()` perform small linear table searches.
- `tune_in()` reads UTF runes through `Bgetrune()`, maps TUNE ranges back to Tamil Unicode sequences, and passes runes to the selected output converter.
- `tune_out()` is a state machine converting Tamil Unicode sequences into TUNE glyph code points.

Control flow:
- TUNE consonant forms in `0xe210..0xe38c` are decoded using the code-point low nibble as a vowel-sign selector.
- Special ligatures/compound Tamil sequences are handled explicitly, including `க்ஷ` and `ஶ்ரீ`.
- Output state tracks a pending consonant/vowel combination and flushes it when the next rune proves it cannot combine.

Risk notes:
- The output path is stateful across calls through static `state` and `lastr`; the final zero-length `OUT` call is required to flush pending state.
- Invalid private-use TUNE runes warn as “not in output cs,” count errors, and may be dropped in clean mode.
