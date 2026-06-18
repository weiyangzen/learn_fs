# File Research: sources/os/plan9/9front/sys/src/cmd/scat/desc.c

Purpose: Static Dreyer/NGC description abbreviation dictionary for `scat`.

Content: `desctab` maps abbreviations and tokens such as object quality marks, brightness terms, compass directions, object morphology, Greek names, and catalog shorthand to prose strings.

Integration: Used by `prose.c` and `scat.c` via `prdesc` to expand compact NGC description strings when printing catalog records.

Risks:
- Table order matters because `prose.c` builds an index by first character and searches adjacent entries with the same initial byte.
- Contains UTF-8 strings for symbols like Greek letters and degrees.
