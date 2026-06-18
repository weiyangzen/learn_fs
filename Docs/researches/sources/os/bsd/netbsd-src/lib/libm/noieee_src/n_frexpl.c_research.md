# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_frexpl.c

Implements `frexpl()` for machines where `long double` is the same format as `double`.

Key behavior:
- Compile-time errors if `__HAVE_LONG_DOUBLE` is defined.
- Delegates to `frexp(x, e)`.
- Exists because `frexp` is in libc while `frexpl` is in libm, so ELF symbol aliases cannot cross libraries.

Important dependencies: `namespace.h` and `<math.h>`.

Notable risks:
- Only valid on platforms without a distinct long-double format.
