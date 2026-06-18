# File Research: sources/os/bsd/netbsd-src/lib/libcurses/unctrl.h

This public header declares the control-character display tables and provides macros for converting byte values to printable forms.

Key declarations:
- `extern const char * const __unctrl[]`
- `extern const unsigned char __unctrllen[]`
- `extern const wchar_t * const __wunctrl[]` when `HAVE_WCHAR` is enabled.

Key macros:
- `unctrl(c)` indexes `__unctrl` with `(unsigned char)c & 0xff`.
- `unctrllen(c)` indexes `__unctrllen` the same way.
- `wunctrl(wc)` indexes `__wunctrl` using the first value field of a curses wide character object.

Integration:
- Included by code needing byte-to-display rendering.
- Pulls in `<wchar.h>` and `<curses.h>` only for wide-character support.

Risks and notes:
- `wunctrl(wc)` assumes a curses wide-character structure with `vals[0]`; it is not a generic `wchar_t` macro.
