# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vfscanf.c

Implements the narrow scanf engine: `__svfscanf()`, `__svfscanf_l()`, and `__svfscanf_unlocked_l()`, with weak aliases for public `vfscanf` forms. It parses flags, width, size modifiers, assignment suppression, integer bases, strings, character classes, `%n`, pointers, and floating-point forms using locale-aware character classification.

Integer scanning uses a finite-state set of flags for signs, zero prefixes, and `0x`; floats are parsed by `parsefloat()` to the last committed valid prefix, pushing extra bytes back with `ungetc()`. `%s`, `%c`, and `%[` support both byte and wide destinations, converting multibyte input with locale-aware `mbrtowc_l()` where needed.
