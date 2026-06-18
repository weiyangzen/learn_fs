# File Research: sources/os/bsd/netbsd-src/lib/libcurses/curses.h

Read completely: 1064 lines.

This is the public libcurses API header. It defines `chtype`, `attr_t`, optional wide-character support, `cchar_t`, boolean constants, key constants from `KEY_MIN` through `KEY_MAX`, `KEY_CODE_YES`, attribute masks, ACS and WACS aliases, color constants, `COLOR_PAIR`, `PAIR_NUMBER`, public globals, `ERR`/`OK`, macro-mode pseudo-functions, function prototypes, wide-character APIs, mouse compatibility APIs, and private-but-user-visible output helper prototypes.

The header defaults `HAVE_WCHAR` on unless `DISABLE_WCHAR` is defined, making wide-character structures and APIs the normal build surface. It encodes attributes and color pairs inside `attr_t`/`chtype` bit masks and exposes the core `WINDOW`/`SCREEN` typedefs as opaque struct names.

Important interactions: nearly every file in this group consumes masks such as `__CHARTEXT`, `__ATTRIBUTES`, `__COLOR`, `WA_ATTRIBUTES`, ACS/WACS macros, and public function prototypes from this header. When `_CURSES_USE_MACROS` is defined, many APIs are direct macro wrappers around window-level functions.

Reliability notes: this header fixes ABI-visible bit assignments and type sizes. The comment requires `attr_t` to match `wchar_t` size to avoid padding in `__LDATA`, which affects hashing, serialization, and cell copying.
