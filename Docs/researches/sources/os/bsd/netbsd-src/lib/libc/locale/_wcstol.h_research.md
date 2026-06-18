# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wcstol.h

Read completely: 161 lines.

This template implements signed wide-string integer conversion for `wcstol`, `wcstoll`, and `wcstoimax`. It validates base, skips locale-aware whitespace, accepts optional sign and `0x` prefixes, auto-detects octal/decimal/hex when base is zero, and accumulates with cutoff/cutlim overflow checks.

Important interactions: concrete wrappers provide return type and min/max macros, and include `__wctoint.h` for digit mapping. The template emits both current-locale and explicit-locale entry points.

Security/reliability notes: overflow sets `errno = ERANGE` and saturates to min/max. Invalid base sets `EINVAL`. The parser is ASCII digit/letter based, not locale-specific for digits.
