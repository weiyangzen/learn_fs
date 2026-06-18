# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/strfmon.c

Implements `strfmon()` and `strfmon_l()` through an internal `vstrfmon_l()` monetary formatter. It parses POSIX monetary conversion flags, field width, left/right precision, national versus international currency symbols, sign positioning, grouping suppression, fill characters, and left justification.

The formatter obtains `struct lconv` from the locale, formats the numeric value with locale-aware `asprintf_l`, inserts monetary decimal/group separators, applies currency/sign ordering from `LC_MONETARY`, and checks output bounds with `E2BIG`. Format errors set `EINVAL`; allocation failures propagate allocation `errno`.

Helper routines normalize locale fields, calculate padding affected by currency/sign placement, and build grouped decimal strings.
