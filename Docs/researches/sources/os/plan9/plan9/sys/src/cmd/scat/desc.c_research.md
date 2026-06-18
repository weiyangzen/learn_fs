# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/desc.c

Defines `desctab`, a large abbreviation-to-prose dictionary for astronomical object descriptions.

Key contents:
- Maps Dreyer/NGC-style abbreviations and symbols to expanded prose, including brightness, size, shape, direction, Greek letters, constellation words, and object descriptors.
- Used by `prose.c` through `prdesc` to expand compact catalog descriptions.

Behavior notes:
- This is data-only C source; it exposes the global `char *desctab[][2]`.
- The table includes UTF-8/Unicode strings such as Greek letters and degree symbols.
