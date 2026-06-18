# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/utf8.c

UTF-8 display-width and locale helper code.

Key responsibilities:
- Carries a Markus Kuhn-derived combining-character interval table.
- Determines whether a UCS code point has zero terminal width.
- Computes wcwidth-like display width, including East Asian wide/fullwidth ranges.
- Decodes UTF-8 byte sequences into UCS values.
- Computes UTF-8 string width in columns.
- Returns UTF-8 character byte length.
- Detects whether the normalized locale codeset is UTF-8.

Important behavior:
- Invalid/truncated UTF-8 is not strictly rejected; missing continuation bytes contribute zero bits.
- Control characters produce width `-1`, which callers ignore for total width.
- Width logic supports older Unicode-era ranges used by Antiword 0.37.

Dependencies:
- Character-set normalization helper, shared integer types/constants.

Research relevance:
- Helps text layout keep sensible column counts for UTF-8 output.
