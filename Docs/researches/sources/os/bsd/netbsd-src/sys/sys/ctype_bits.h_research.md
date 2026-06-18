# File Research: sources/os/bsd/netbsd-src/sys/sys/ctype_bits.h

Defines character classification bit masks and declares ctype lookup tables.

Key content:
- Classification bits: alpha, control, digit, graph, lower, punct, space, upper, xdigit, blank, print, ideogram, special, phonogram.
- Declares active locale/table pointers: `_ctype_tab_`, `_tolower_tab_`, `_toupper_tab_`.
- Declares C locale backing tables: `_C_ctype_tab_`, `_C_toupper_tab_`, `_C_tolower_tab_`.

Important behavior:
- Uses `__BEGIN_DECLS`/`__END_DECLS` for C++ compatibility.
- Shared by inline ctype macro definitions.
