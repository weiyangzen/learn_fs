# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/vasnprintf.h

Purpose: declares dynamically allocated narrow formatted-string helpers.

Important APIs/types/functions: `asnprintf(resultbuf, lengthp, format, ...)` and `vasnprintf(resultbuf, lengthp, format, va_list)` return a pointer to a NUL-terminated formatted string, either reusing `resultbuf` or allocating with `malloc`. On success `*lengthp` receives the byte count excluding the trailing NUL. GCC printf-format attributes are provided when available.

State and persistence: no state. Ownership is returned to the caller when the returned pointer differs from `resultbuf`.

Dependencies and integration: includes `stdarg.h` and `stddef.h`; consumed by `vasnprintf.c`, `printf.c`, and callers needing XSI positional formatting support.

Risks and test signals: callers must pass a valid `lengthp` and free allocated results. Test compiler attribute compatibility, C++ linkage, result buffer reuse, and error returns.
