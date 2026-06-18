# File Research: sources/virtualization/guestfs-tools/gnulib/lib/c-ctype.h

Locale-independent character classification helpers.

Purpose:
- Mirrors common `<ctype.h>` functions but hardwires C/POSIX locale behavior.
- Supports ASCII and EBCDIC variants; errors out for unsupported character sets.
- Accepts values in `unsigned char` or `char` range without requiring caller casts.

Functions:
- `c_isalnum`, `c_isalpha`, `c_isascii`, `c_isblank`, `c_iscntrl`, `c_isdigit`, `c_isgraph`, `c_islower`, `c_isprint`, `c_ispunct`, `c_isspace`, `c_isupper`, `c_isxdigit`.
- `c_tolower`, `c_toupper`.

Research relevance: stable parsing helper; used where locale-sensitive `ctype.h` behavior would be incorrect.
