# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scantab.c

Defines `scan_char_array`, the token scanner lookup table described by `scanchar.h`. The table classifies stream exceptions, ASCII control characters, printable ASCII, binary token bytes 128-159, and high bytes 160-255.

Digits map to radix values, letters map to radix values through base 36 where appropriate, PostScript delimiters map to `ctype_other`, whitespace maps to `ctype_space`, and binary token marker bytes map to `ctype_btoken`.

Dependencies include `stdpre.h`, `scommon.h`, and `scanchar.h`.

This is scanner data for Ghostscript language parsing.
