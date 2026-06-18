# File Research: sources/os/bsd/netbsd-src/lib/libcurses/cchar.c

Read completely: 139 lines.

This file implements complex-character conversion helpers: `getcchar`, `setcchar`, and internal `__cursesi_chtype_to_cchar`.

`getcchar` reports or copies the wide-character sequence stored in a `cchar_t`, returning the element count when the caller passes `wch == NULL`. When copying, it requires `attrs` and `color_pair`, returns attributes, extracts the color pair when colors are active, copies `vals`, and null-terminates the output string.

`setcchar` builds a `cchar_t` from a wide-character string, attributes, and color pair. It rejects unsupported `opts`, strings longer than `CCHARW_MAX`, and invalid multi-character starts. It truncates at the first later spacing character because only a base character plus nonspacing characters are represented. `__cursesi_chtype_to_cchar` converts ordinary `chtype` values or internal WACS-marked ACS values into `cchar_t`.

Important interactions: uses `__using_color`, `PAIR_NUMBER`, `COLOR_PAIR`, `__ACS_IS_WACS`, `_wacs_char`, and `wcwidth`.

Reliability notes: callers must pass a valid `wcval`/`wch`; there is no null validation for those required inputs. `setcchar` uses `wcslen`, so an unterminated input string is unsafe.
