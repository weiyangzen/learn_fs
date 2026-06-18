# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/utf2ksym.h

Generated static lookup table converting Unicode runes to X11 keysyms for VNC client-side keyboard output.

Key contents:
- Defines `static ulong utf2ksym[]`.
- Sparse designated indexes cover many of the same script and symbol ranges as `ksym2utf.h`: Latin extended, Japanese kana, Arabic/Persian, Cyrillic, Greek, math, box drawing, punctuation, Hebrew, Thai, Korean Jamo, Vietnamese, currency, Armenian, Georgian, and private/special symbols.
- Used by `kbdv.c` to send keysyms that VNC servers expect instead of raw Unicode code points where a mapping exists.

Important behavior:
- Indexed directly by Unicode rune when the rune is within `nelem(utf2ksym)` and the entry is nonzero.
- ASCII and unmapped runes are sent as their rune value.

Risks:
- Reverse mapping loses duplicates: when several keysyms map to one rune, only one designated rune entry can be used.
- Sparse Unicode-indexed array is simple but memory-heavy.
