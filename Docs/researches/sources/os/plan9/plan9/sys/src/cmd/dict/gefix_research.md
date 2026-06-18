# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/gefix

This rc script normalizes German/English-style raw dictionary index data.

Key behaviors:
- Removes trailing whitespace and drops lines without tabs.
- Removes specific encoded noise sequences and quote markers.
- Normalizes hyphenated tab fields and trailing hyphens.
- Expands parenthesized forms.
- Expands `(r, s)` endings into base, `r`, and `s` variants.
- Emits extra `ss` spellings for entries containing `ß`.
- Converts tab/comma-separated values into `term<TAB>offset`, lowercases, and sorts uniquely.

Notable implementation details:
- Uses two similar `sed` expansion passes followed by AWK, `tr`, and `sort`.
- Tailored to a particular raw index format with German orthographic variants.
