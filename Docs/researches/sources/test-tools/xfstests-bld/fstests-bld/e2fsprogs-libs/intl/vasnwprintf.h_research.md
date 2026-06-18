# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/vasnwprintf.h

Purpose: declares dynamically allocated wide-character formatted-string helpers.

Important APIs/types/functions: `asnwprintf(resultbuf, lengthp, format, ...)` and `vasnwprintf(resultbuf, lengthp, format, va_list)` mirror the narrow API but operate on `wchar_t` strings. Success returns either the caller buffer or a malloc-allocated buffer and stores the resulting wide-character count excluding the NUL in `*lengthp`.

State and persistence: no state; caller owns any allocated result.

Dependencies and integration: includes `stdarg.h` and `stddef.h` for `wchar_t`/`size_t`. Used by `vasnprintf.c` when `WIDE_CHAR_VERSION` is set and by wide printf wrappers in `printf.c`.

Risks and test signals: return length semantics must stay in wide characters, not bytes. Test wide literals, wide strings/chars, buffer reuse, C++ linkage, and platform differences in `swprintf`/`_snwprintf`.
