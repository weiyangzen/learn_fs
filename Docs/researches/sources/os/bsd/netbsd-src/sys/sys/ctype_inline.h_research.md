# File Research: sources/os/bsd/netbsd-src/sys/sys/ctype_inline.h

Defines inline macro implementations for classic ctype and case conversion APIs.

Key content:
- Includes `sys/cdefs.h`, `sys/featuretest.h`, and `sys/ctype_bits.h`.
- Macros: `isalnum`, `isalpha`, `iscntrl`, `isdigit`, `isgraph`, `islower`, `isprint`, `ispunct`, `isspace`, `isupper`, `isxdigit`, `tolower`, `toupper`.
- XOpen/NetBSD extensions: `isascii`, `toascii`, `_tolower`, `_toupper`.
- C99/POSIX/NetBSD `isblank` exposure.

Important behavior:
- Uses `(_ctype_tab_ + 1)[c]` table indexing, supporting EOF-style indexing conventions.
- Namespace exposure is controlled by feature-test macros.
