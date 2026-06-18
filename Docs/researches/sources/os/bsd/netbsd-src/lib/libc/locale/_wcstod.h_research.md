# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wcstod.h

Read completely: 146 lines.

This template implements `wcstof`, `wcstod`, and `wcstold` families. It skips wide whitespace, converts the remaining wide string to multibyte with `wcstombs_l`, calls the configured `strto*_l` function, and maps the resulting multibyte end pointer back to a wide-character end pointer.

Important interactions: concrete files define `_FUNCNAME`, `_RETURN_TYPE`, and `_STRTOD_FUNC` before including this template. It uses `_current_locale()` for non-`_l` wrappers and `setlocale_local.h` for locale access.

Security/reliability notes: handles conversion and allocation failure by returning zero and setting `endptr` to the original input. The end-pointer mapping has an explicit `XXX` assumption that each wide character is one byte in the converted portion, which can be wrong for multibyte encodings.
