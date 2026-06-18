# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/out2window.c

Text-window layout adapter that turns Antiword output runs into diagram lines, aligned paragraphs, heading numbers, and fallback table text.

Key responsibilities:
- Emits linked `output_type` string runs into a `diagram_type`, preserving font/style/color metadata.
- Computes net line width, strips trailing whitespace, applies left/center/right alignment, and justifies text by distributing spaces.
- Maintains nine heading counters and renders outline numbering in Arabic, Roman, alpha, and outline-number styles.
- Sets left indentation in draw units.
- Removes Word table-row terminators and formats table rows into fixed-width text columns when XML table handling does not consume them.
- Calculates byte-safe wrapping for multi-byte/UTF-8 strings using column counts and character-length helpers.

Dependencies:
- Uses output/backend dispatcher calls such as `vMove2NextLine`, `vSubstring2Diagram`, and `bAddTableRow`.
- Uses style, section, and row metadata from Antiword parsing layers.

Notable risks:
- Justification rewrites run storage in place and depends on accurate string widths.
- Table rendering assumes fixed-width font behavior and warns/skips when parsed column counts do not match row metadata.
- Heading counters are static global state reset by `vResetStyles()`.
