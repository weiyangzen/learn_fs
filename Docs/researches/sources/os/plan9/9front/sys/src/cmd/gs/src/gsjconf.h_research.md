# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsjconf.h

Ghostscript-specific `jconfig.h` configuration wrapper for Independent JPEG Group code.

Key behavior:
- Includes `arch.h`; notes that `stdpre.h` is concatenated externally during IJG build setup rather than directly included here.
- Enables prototype, unsigned char, and unsigned short support where available.
- Enables `HAVE_STDDEF_H` and `HAVE_STDLIB_H` under `__STDC__`.
- Disables BSD strings, sys/types, far pointers, short external names, and incomplete-type workaround flags.
- On very small `int` platforms, caps `MAX_ALLOC_CHUNK` at `0xfff0`.
- Under `JPEG_INTERNALS`, defines `RIGHT_SHIFT_IS_UNSIGNED` based on `ARCH_ARITH_RSHIFT`.

Dependencies:
- Depends on Ghostscript architecture feature macros, especially `ARCH_SIZEOF_INT` and `ARCH_ARITH_RSHIFT`.

Research notes:
- This is build-configuration glue, not runtime code.
- It narrows IJG feature assumptions to match Ghostscript’s portability layer.
