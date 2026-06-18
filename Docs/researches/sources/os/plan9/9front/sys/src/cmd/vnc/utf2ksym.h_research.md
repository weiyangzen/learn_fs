# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/utf2ksym.h

## Role

`utf2ksym.h` is a static lookup table mapping Unicode runes to X11/VNC keysyms for viewer-side keyboard event generation.

## Contents

- Defines `static ulong utf2ksym[]`.
- Covers many of the same character families as `ksym2utf.h`: Latin extended, Japanese kana, Arabic/Persian, Cyrillic, Greek, symbols, Hebrew, Thai, Korean Jamo, Armenian, Georgian, Vietnamese, and currency symbols.
- Used by `kbdv.c` to convert Plan 9 keyboard runes into the keysyms expected by remote VNC servers.

## Notable Limitations And Risk Areas

- The reverse mapping cannot preserve all duplicates from `ksym2utf.h`; where multiple keysyms map to one rune, one mapping wins.
- Unmapped runes are sent as their rune value or through explicit special-key tables.
- This is static keysym conversion, not locale-aware keyboard layout processing.
