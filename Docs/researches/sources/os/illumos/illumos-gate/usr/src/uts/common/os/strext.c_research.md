# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/strext.c

## Purpose

`strext.c` provides small SunOS-specific kernel string/formatting helpers that are not part of the shared standalone/libc string implementation. The file is compact and self-contained, relying mainly on `vsnprintf()`, kernel allocation, and simple character scanning.

## Entry Points

- `vsprintf_len(size_t buflen, char *buf, const char *fmt, va_list args)`: historical bounded formatting wrapper. It calls `vsnprintf(buf, buflen, fmt, args)` and returns `buf`.
- `sprintf_len(size_t buflen, char *buf, const char *fmt, ...)`: variadic companion to `vsprintf_len()`, also returning `buf`.
- `numtos(unsigned long num, char *s)`: converts an unsigned long to a decimal NUL-terminated string. It uses a local reverse buffer and assumes the caller provided enough output space.
- `stoi(char **str)`: parses decimal digits from `*str`, returns the integer value, and updates `*str` to the first non-digit. It performs no overflow checking.
- `strnrchr(const char *sp, int c, size_t n)`: bounded reverse character search over at most `n` non-NUL characters. Unlike a raw bounded memory search, a terminating NUL stops the scan and is not itself considered part of the searchable string.
- `sprintf(char *buf, const char *fmt, ...)`: kernel DDI-compatible `sprintf()` that returns `buf`, implemented via `vsnprintf(buf, INT_MAX, ...)`.
- `vsprintf(char *buf, const char *fmt, va_list args)`: `vsprintf()` variant with the same return convention and effectively unbounded `INT_MAX` limit.
- `kmem_asprintf(const char *fmt, ...)`: allocates a formatted string with `kmem_alloc(KM_SLEEP)`, sizing it through a first `vsnprintf(NULL, 0, ...)` pass. The comment states callers must free the exact returned string with `strfree()`.

## Dependencies

Headers used are `sys/types.h`, `sys/cmn_err.h`, `sys/systm.h`, and `sys/varargs.h`. Runtime dependencies are kernel `vsnprintf()`, `kmem_alloc()`, `KM_SLEEP`, `INT_MAX`, and the corresponding string-freeing convention for `kmem_asprintf()` callers.

## Risks And Maintenance Notes

The historical formatting helpers return the destination buffer rather than the formatted length. Callers may depend on this DDI/SunOS behavior, so replacing them with standard libc-like return values would be ABI-visible.

`numtos()` and `stoi()` are intentionally minimal. `numtos()` has no output-size parameter, and `stoi()` does no overflow detection and accepts only decimal digits. They should only be used where callers already bound inputs and storage.

`sprintf()` and `vsprintf()` pass `INT_MAX` to `vsnprintf()`, so safety depends on the caller supplying a sufficiently large buffer. New code should prefer bounded helpers where practical.

`kmem_asprintf()` performs two formatting passes and allocates with sleeping semantics. It is unsuitable for contexts that cannot sleep, and callers must use the expected freeing path rather than assuming a normal static or stack buffer.
