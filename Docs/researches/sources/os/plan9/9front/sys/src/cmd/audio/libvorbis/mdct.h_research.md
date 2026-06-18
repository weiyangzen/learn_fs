# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/mdct.h

Header for MDCT lookup state and transform prototypes.

Important contents:
- Optional `MDCT_INTEGERIZED` macro branch defines integer data types, trig constants, conversion, multiply-normalization, and halving macros.
- Default branch defines float data/register types and float constants.
- Defines `mdct_lookup` with block size, log2 size, trig table, bit-reversal table, and scale.
- Declares `mdct_init()`, `mdct_clear()`, `mdct_forward()`, and `mdct_backward()`.

Integration points:
- Included by `mdct.c`, `envelope.h`, and transform users.

Risk and review signals:
- Integerized path is commented as potentially rough/noisy and is disabled by default.
- Header exposes implementation macros that affect ABI/behavior of `mdct_lookup`.

Filesystem relevance:
- No filesystem logic.
