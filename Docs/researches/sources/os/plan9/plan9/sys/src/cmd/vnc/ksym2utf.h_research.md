# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/ksym2utf.h

Generated static lookup table converting X11 keysyms to Unicode runes for VNC server-side input.

Key contents:
- Defines `static ulong ksym2utf[]`.
- Sparse designated indexes cover X11 keysym ranges for Latin extended letters, Japanese kana, Arabic/Persian, Cyrillic, Greek, mathematical symbols, box drawing, punctuation, Hebrew, Thai, Korean Jamo, Vietnamese, currency symbols, Armenian, Georgian, and other extended ranges.
- Used by `kbds.c` after special-key handling to convert incoming VNC/X keysyms into Plan 9 runes.

Important behavior:
- The array is indexed directly by keysym when the keysym is within `nelem(ksym2utf)` and the entry is nonzero.
- ASCII keysyms pass through without table lookup.

Risks:
- Sparse table size is determined by the largest designated index, so it is convenient but memory-heavy compared with a compact map.
- Reverse mapping is not perfectly one-to-one for duplicate Unicode values.
