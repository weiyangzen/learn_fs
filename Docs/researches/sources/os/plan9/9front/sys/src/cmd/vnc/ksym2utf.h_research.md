# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/ksym2utf.h

## Role

`ksym2utf.h` is a static lookup table mapping X11/VNC keysyms to Unicode runes for server-side keyboard input conversion.

## Contents

- Defines `static ulong ksym2utf[]`.
- Covers Latin extended characters, Japanese kana, Arabic/Persian, Cyrillic, Greek, mathematical symbols, box drawing, typographic symbols, Hebrew, Thai, Korean Jamo, Armenian, Georgian, Vietnamese, currency symbols, and other X11 keysym ranges.
- Used by `kbds.c` to translate incoming VNC key symbols into Plan 9 runes before writing `/dev/kbdin`.

## Notable Limitations And Risk Areas

- This is sparse designated-initializer data; unmapped entries default to zero and are treated as unsupported.
- It is not a full Unicode keyboard layout engine; it only maps the keysyms listed.
- Some symbols can have multiple possible X11 keysym origins, so reverse mapping is not always one-to-one.
