# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_none.c

Read completely: 590 lines.

This implements the built-in `NONE` ctype and stdenc modules, effectively a byte-preserving single-byte encoding. The ctype half implements `mblen`, `mbrlen`, `mbrtowc`, `mbsrtowcs`, `mbsnrtowcs`, `mbtowc`, `wcrtomb`, `wcsrtombs`, `wcsnrtombs`, `wcstombs`, `wctomb`, `btowc`, and `wctob`. The stdenc half exposes the same behavior through Citrus standard-encoding callbacks.

Key behavior: `MB_CUR_MAX` is 1, states are always initial/stateless, bytes map to wide characters via `(unsigned char)`, and wide characters are only encodable if they fit in 8 bits. Invalid wide characters return `EILSEQ`; too-small output buffers in stdenc return `E2BIG`; incomplete input returns the conventional `(size_t)-2` for restartable interfaces.

Important interactions: `_citrus_stdenc_default` in `citrus_stdenc.c` uses `_citrus_NONE_stdenc_ops` and `_citrus_NONE_stdenc_traits`. The header `citrus_none.h` exports those operation tables.

Security/reliability notes: this is a low-complexity fallback encoding. The conversion functions consistently guard 8-bit bounds before writing. The logic relies on callers providing valid result pointers, as enforced only by convention or `_DIAGASSERT` in some paths.
