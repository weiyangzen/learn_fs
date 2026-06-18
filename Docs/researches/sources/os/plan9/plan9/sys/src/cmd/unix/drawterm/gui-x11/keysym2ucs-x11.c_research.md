# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/keysym2ucs-x11.c

Public-domain generated X11 keysym-to-Unicode conversion table from Markus Kuhn’s xterm-era mapping.

Key responsibilities:
- Defines sorted `keysymtab[]` pairs mapping non-Latin-1 X11 keysyms to UCS values.
- Covers many scripts and symbol ranges, including Latin extended, Kana, Arabic, Cyrillic, Greek, technical symbols, box drawing, publishing symbols, Hebrew, Thai, Hangul, and Euro/OE additions.
- Implements `keysym2ucs(KeySym)` with Latin-1 direct mapping, direct UCS keysyms in `0x01000000..0x01ffffff`, and binary search over the table.

Role in this group:
- Used by `gui-x11/x11.c` to translate non-ASCII/non-ISO-1 keysyms into Plan 9 rune values.

Notable risks:
- The file is generated and old; newer X11 keysyms or Unicode assignments may be absent.
- The table must remain sorted for binary search correctness.
