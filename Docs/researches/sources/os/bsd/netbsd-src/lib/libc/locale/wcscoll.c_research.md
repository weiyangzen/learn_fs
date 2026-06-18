# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcscoll.c

Read completely: 56 lines.

This file implements `wcscoll` and `wcscoll_l` as simple `wcscmp` wrappers. A comment notes that `LC_COLLATE` should be implemented.

Important interactions: uses `_current_locale()` for the non-`_l` wrapper but ignores the locale argument.

Security/reliability notes: no locale collation support; sorting behavior is code-point/wide-character order rather than locale collation order.
