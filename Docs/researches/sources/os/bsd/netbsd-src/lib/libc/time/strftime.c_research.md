# File Research: sources/os/bsd/netbsd-src/lib/libc/time/strftime.c

## Purpose
Implements NetBSD libc `strftime`, `strftime_l`, `strftime_z`, and `strftime_lz`: formatting a broken-down `struct tm` into locale-aware text, including timezone-aware `%Z`, `%z`, and epoch-seconds `%s` handling.

## Public Entry Points
- `strftime_z(timezone_t sp, char *s, size_t maxsize, const char *format, const struct tm *t)`: timezone-object formatting using the current locale.
- `strftime_lz(timezone_t sp, char *s, size_t maxsize, const char *format, const struct tm *t, locale_t loc)`: timezone-object plus explicit locale.
- `strftime(char *s, size_t maxsize, const char *format, const struct tm *t)`: locks local timezone state, refreshes it with `tzset_unlocked`, and delegates to `strftime_z`.
- `strftime_l(...)`: same as `strftime`, but with explicit locale.

The file defines weak aliases for the locale and timezone variants when supported.

## Formatting Engine
`_fmt` is the recursive formatter. It scans the format string and appends into the caller’s bounded buffer. Supported conversions include:
- Locale names and formats: `%A`, `%a`, `%B`, `%b`, `%h`, `%c`, `%x`, `%X`, `%r`, `%p`.
- Date/time numeric fields: `%C`, `%d`, `%e`, `%F`, `%H`, `%I`, `%j`, `%k`, `%l`, `%M`, `%m`, `%R`, `%S`, `%T`, `%U`, `%W`, `%w`, `%u`, `%v`, `%Y`, `%y`.
- ISO week/year: `%V`, `%G`, `%g`.
- Timezone and epoch: `%Z`, `%z`, `%s`.
- Literals and spacing: `%%`, `%n`, `%t`, `%+`.
- Padding modifiers: `%-`, `%_`, `%0`.
- Alternative modifiers: `%E`, `%O`, parsed for standards compliance though not fully localized with alternative representations.

`_add` appends literal text with bounds checks. `_conv` formats integers using `snprintf_l`. `_yconv` implements century/year formatting so `%C%y` composes consistently with `%Y`, including unusual negative or large years.

## Locale Integration
Uses NetBSD `_TimeLocale` from `sys/localedef.h`, reached via `_TIME_LOCALE(loc)`. Locale data supplies day names, month names, AM/PM strings, and date/time format templates. The code maps `c_fmt` to `d_t_fmt`.

## Timezone Handling
For `%Z`, the formatter prefers `tm_zone` when available. Otherwise it queries the timezone object with `tzgetname`, falling back across DST states if needed.

For `%z`, it prefers `tm_gmtoff`. If unavailable, it either uses compatibility globals or computes the offset by comparing `mktime_z` and `timegm`. It preserves negative-zero style behavior when the abbreviation indicates an unspecified offset.

For `%s`, it reconstructs a `time_t` from the supplied `struct tm` using `timeoff` when `tm_gmtoff` is available, otherwise `mktime_z`. To avoid overflow in this path, the file may include `localtime.c` internally with `USE_TIMEX_T` when native `mktime` might overflow.

## Buffer and Error Behavior
`strftime_lz` returns `0` and sets `errno = ERANGE` if output fills the buffer. On success, it restores the caller’s prior `errno`, null-terminates the buffer, and returns the number of bytes written excluding the terminator.

## Notable Risks and Edge Cases
- `%s` may compile in a special widened internal time implementation via `localtime.c`.
- The public `strftime` wrappers depend on `__lcl_lock`, `__lcl_ptr`, and `tzset_unlocked` from `localtime.c`; this couples formatting to libc timezone state.
- Alternate era/numeric locale modifiers are accepted only to the extent supported by the local locale structures.
- `%Z`/`%z` behavior differs depending on whether `tm_zone`/`tm_gmtoff` are available and initialized.
