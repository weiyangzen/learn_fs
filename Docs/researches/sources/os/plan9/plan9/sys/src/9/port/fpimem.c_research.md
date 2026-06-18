# File Research: sources/os/plan9/plan9/sys/src/9/port/fpimem.c

Purpose: Memory-format conversions between native single/double/integer values and the `Internal` format used by the floating-point interpreter.

Key logic:
- `fpis2i` and `fpid2i` decode IEEE single/double bit layouts into `Internal`.
- `fpiw2i` and `fpiv2i` convert signed 32-bit and 64-bit integers to `Internal`.
- `fpii2s` and `fpii2d` round and encode internal values to single/double memory formats.
- `fpii2w` and `fpii2v` round and convert internal values back to signed integer types, saturating on overflow.

Dependencies and integration:
- Includes `fpi.h`; explicitly depends on memory format, not CPU arithmetic.

Risks and notes:
- Output conversions mutate the supplied `Internal`; caller should pass a disposable copy.
- 64-bit conversion uses shifts that assume the interpreter’s fraction constants.
