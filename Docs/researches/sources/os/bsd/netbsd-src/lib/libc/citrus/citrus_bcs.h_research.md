# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs.h

Declares and defines inline predicates/conversions for the POSIX-like basic character set.

Key behavior:
- Inline predicates for blank, EOL, space, digit, upper, lower, alpha, alnum, and xdigit.
- Inline uppercase/lowercase transforms that do not accept EOF.
- Declarations for BCS string comparison, whitespace scanners, case conversion, and BCS-only `strtol`/`strtoul`.

Notable detail:
- The header explicitly distinguishes these helpers from `ctype.h`: they operate on `uint8_t` characters and are not locale-dependent.
