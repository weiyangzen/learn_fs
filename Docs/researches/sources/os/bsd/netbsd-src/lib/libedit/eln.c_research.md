# File Research: sources/os/bsd/netbsd-src/lib/libedit/eln.c

This file implements narrow-character compatibility wrappers around libedit's wide-character core APIs.

Key entry points:
- `el_getc()` calls `el_wgetc()` and converts one wide character to a single byte with `wctob()`.
- `el_push()` decodes a narrow string and calls `el_wpush()`.
- `el_gets()` calls `el_wgets()`, converts the returned line to multibyte, and adjusts `nread` to byte length.
- `el_parse()` decodes argv and calls `el_wparse()`.
- `el_set()` maps narrow varargs options to wide/internal operations.
- `el_get()` maps wide/internal results back to narrow API types.
- `el_line()` converts `LineInfoW` to legacy byte-offset `LineInfo`.
- `el_insertstr()` and `el_replacestr()` decode narrow strings and call wide insertion/replacement.

Important behavior:
- `EL_BIND`, `EL_TELLTC`, `EL_SETTC`, `EL_ECHOTC`, and `EL_SETTY` decode up to 20 narrow strings and call the same underlying map/terminal/tty handlers as `el_wset()`.
- `EL_ADDFN` decodes name/help strings but leaves the function pointer unchanged.
- `EL_HIST` marks `NARROW_HISTORY`, causing history conversion through `hist_convert()`.
- `el_line()` computes byte offsets for cursor and lastchar by summing encoded widths.

Risks and notes:
- `el_getc()` fails with `ERANGE` when a wide character cannot be represented as one byte.
- Returned converted strings use `el_lgcyconv`, a reusable buffer that is overwritten by later conversions.
- Varargs type correctness is critical.
